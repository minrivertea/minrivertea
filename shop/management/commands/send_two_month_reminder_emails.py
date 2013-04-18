from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime, timedelta

from shop.models import Order, Shopper, Product, UniqueProduct
from emailer.views import _send_two_month_reminder_email, _admin_cron_update


class Command(NoArgsCommand):
    help = "Sends out a 2 month reminder email if someone hasn't ordered for 2 months "

    def handle_noargs(self, **options):
        
        # 1. GET SHOPPERS WHO BOUGHT SOMETHING MORE THAN 2 MONTHS AGO
        two_months_ago = (datetime.now() - timedelta(days=60))
        old_orders = Order.objects.filter(date_paid__lte=two_months_ago, is_paid=True, is_giveaway=False)
        new_orders = Order.objects.filter(date_paid__gte=two_months_ago, is_paid=True, is_giveaway=False)
        
        
        orders = []
        
        
        seen = {}
        shoppers = []
        
        for o in orders:
            marker = o.owner.email
            if marker in seen: continue
            seen[marker] = 1
            shoppers.append(o.owner) 
        
        print shoppers
        
        
        # set a date range of the last 2 months
        start_date = (datetime.now() - timedelta(days=60)) # two months ago
        end_date = datetime.now() # now
        
        # our empty dictionary
        relevant_orders = []

        for shopper in shoppers:
            orders = Order.objects.filter(
                owner=shopper, 
                is_paid=True, 
                status=Order.STATUS_SHIPPED
            ).exclude(invoice_id__startswith='WL').order_by('-date_confirmed')
                
            if orders.count() == 0:
                pass # because they haven't actually completed any orders
            else:
                # if they've made a new order in the last 2 months, exclude them
                if len(orders.filter(date_paid__range=(start_date, end_date))) > 0: 
                    pass
                else:                
                    # if no orders in the last 2 months, email them.
                    order = orders[0]
                    relevant_orders.append(order)
        
        
        # now lets do some slow and painful filtering...
        new_orders = []
        removed = []
        for order in relevant_orders:
            for item in order.items.all():
            
                if order in new_orders or order in removed:
                    break
                  
                # filter the order out if any UniqueProduct is not active     
                if item.item.is_active == False:
                    if order not in removed:
                        removed.append(order)
                        break
                        
                # filter out the order if their item quantity is more than we have available
                if item.quantity > item.item.available_stock:
                    if order not in removed:
                        removed.append(order)
                        break
                
                # filter out orders where the parent product of any item is marked as 'coming soon' 
                if item.item.parent_product.coming_soon == True:
                    if order not in removed:
                        removed.append(order)
                        break
                
                # if everything is good, then send them an email!
                new_orders.append(order)

            
        # finally send them the email!
        
        emails_sent = []
        for x in new_orders:
            if _send_two_month_reminder_email(x) == True:
                emails_sent.append(x)
            
        if len(emails_sent) > 0:     
            _admin_cron_update(data=emails_sent, subject_line="Minrivertea.com - 2 month reminder emails sent")


        
           
                   
     
                    


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