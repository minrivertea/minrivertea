from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime, timedelta

from minriver.shop.models import Order, Shopper, Product, UniqueProduct
from minriver.shop.emails import _send_two_month_reminder_email, _admin_cron_update


class Command(NoArgsCommand):
    help = 'Sends out all timed emails'

    def handle_noargs(self, **options):
        
        # get all the shoppers
        shoppers = Shopper.objects.all()
        
        # set a date range of the last 2 months
        start_date = (datetime.now() - timedelta(days=60)) # two months ago
        end_date = datetime.now() # now
        
        # filter out shoppers who didn't buy anything outside of the last 2 months.
        relevant_orders = []

        # find shoppers who have made proper paid orders and haven't receive a reminder before
        for shopper in shoppers:
            # if we've ever sent them a reminder at anytime anywhere, DON'T send another!
            if shopper.reminder_email_sent:
                pass
            else:
                orders = Order.objects.filter(owner=shopper, is_paid=True, status=Order.STATUS_SHIPPED).order_by('-date_paid')
                if orders.count() == 0:
                    pass
                else:
                    # if they've made a new order in the last 2 months, exclude them
                    if len(orders.filter(date_paid__range=(start_date, end_date))) > 0:
                        pass
                    else:                
                        # if no orders in the last 2 months, email them.
                        order = orders[0]
                        relevant_orders.append(order)
            
        
        # so send them the email!
        emails_sent = []
        for x in relevant_orders:
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