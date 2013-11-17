from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime, timedelta

from shop.models import Order, Shopper, Product, UniqueProduct
from logistics.models import CustomerPackage
from emailer.views import _reorder_email, _admin_cron_update


class Command(NoArgsCommand):
    help = "Sends out a 2 month reminder email if someone hasn't ordered for 2 months "

    def handle_noargs(self, **options):
        
        # GATHER UP A LIST OF PACKAGES SENT MORE THAN 2 MONTHS AGO
        # THAT HAVEN'T ALREADY RECEIVED A REORDER EMAIL
        two_months = (datetime.now() - timedelta(days=60))
        four_months = (datetime.now() - timedelta(days=120))
        packages = CustomerPackage.objects.filter(
                posted__range=(four_months, two_months), 
                reorder_email_sent__isnull=True
                ).order_by('-posted')
                
        # UNIQUIFY THE LIST BASED ON SHOPPER
        unique_packages = []
        seen = {}
        for p in packages:
            marker = p.order.owner.email
            if marker in seen: continue
            seen[marker] = 1
            unique_packages.append(p)
        
        
        # NOW START THE PROCESSING        
        admin_data = []
        for p in packages:
            
            # IF THE CUSTOMER HAS ALREADY ORDERED SINCE THEN, LET'S STOP THIS
            recent_paid_orders = Order.objects.filter(
                    owner=p.order.owner, 
                    date_paid__isnull=False, 
                    status=Order.STATUS_PAID
                    )
            if recent_paid_orders.count() > 0:
                print p
                print "   this one has already ordered since"
                continue
                
            
            # DO SOME FILTERING BASED ON THE ITEMS IN THEIR BASKET
            exclude = False
            for x in p.get_items():
                
                # IF THIS UNIQUE PRODUCT ISN'T ACTIVE FOR ANY REASON
                if x.unique_product.is_active == False:
                    exclude = True
                    break
                
                # IF WE DON'T HAVE ENOUGH STOCKS
                items = p.get_items().filter(unique_product=x.unique_product)
                stocks = x.unique_product.stocks()
                if stocks.count() < items.count():
                    exclude = True
                    break
                
                if x.unique_product.parent_product.is_active == False:
                    exclude = True
                    break
            
            # IF ANY OF HTE EXCLUSIONS MATCHED, THEN PASS THIS PACKAGE
            if exclude == True:
                continue
            
            
            # OTHERWISE, LET'S SEND THEM AN EMAIL!
            _reorder_email(p.order)
            p.reorder_email_sent = datetime.now()
            p.save()
            admin_data.append(p)

            
        if len(admin_data) > 0:     
            _admin_cron_update(data=admin_data, subject_line="minrivertea.com - 2 month reminder emails sent")

                    


""" This function should do these things in order:

 1. Get a list of customers that have not ordered for more than 2 months.
 2. Check if the products they ordered are still in stock.
 3. Send them a two_month_reminder email
 4. Update their order.
 
 The rules of this reminder email are that if a customer has ordered from us in the last 2 months, they don't
 get another email. Similarly, if they've EVER received a reminder from us in the past, they don't get
 any more (no need to keep spamming them).
 
 There's also some logic in the _send_two_month_reminder_email function that suggests replacements if a product
 is not available anymore (or out of stock etc.)
 
"""