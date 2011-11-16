from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime, timedelta

# import various bits and pieces
from minriver.shop.models import Order, Review
from minriver.shop.emails import _product_review_email, _admin_cron_update


# this sends out the first 'review' email after the order was shipped.
class Command(NoArgsCommand):
    help = 'Sends out all timed emails'

    def handle_noargs(self, **options):
        # we need to get hold of orders that have DEFINITELY been paid and shipped.
        items = []
        for order in Order.objects.filter(
                is_paid=True,
                is_giveaway=False,
                status=Order.STATUS_SHIPPED, 
                review_email_sent=False,
         ):
            if order.date_shipped is None:
                # IMPORTANT this stops old orders with no shipping date from being included.
                pass
            else: 
                # if 1 week after the order was shipped is great than the time now... do this...           
                if (order.date_shipped + timedelta(days=7)) < datetime.now():
                    # if it's been 1 week since the order was shipped, send the email.
                    # note that the function below updates and saves the 'review_email_sent' boolean, 
                    # so we don't need to do it twice.
                    _product_review_email(order.id)
                    items.append(order)
        
        #finally, if there were any emails sent, then drop the admin user an email too
        if items:
            _admin_cron_update(data=items, subject_line="Minrivertea.com - review emails sent today")      
                    


""" This function should do these things in order:

 1. Get a list of orders that have been shipped, where no review email has been sent to the customer
 2. Check if the shipping date is more than 7 days before
 3. If it has been 7 days since the item was shipped, send the customer an email.
 4. Send the admin user a list of the emails sent
 
"""