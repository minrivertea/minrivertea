from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime, timedelta

# import various bits and pieces
from minriver.shop.models import Order, Review
from minriver.shop.emails import _order_reminder_email, _admin_cron_update
from datetime import datetime, timedelta
from django.db.models import Q

# this sends out the first 'review' email after the order was shipped.
class Command(NoArgsCommand):
    help = 'Sends out all timed emails'

    def handle_noargs(self, **options):
        # get a list of orders that have been abandoned in the last 1 day.
        
        start_date = (datetime.now() - timedelta(days=1)) # one day ago (because the Cron runs everyday)
        end_date = datetime.now() # now
        
        # let's do the query, getting the most recent abandoned order and filtering out duplicates (duplicate owners)
        seen = {}
        items = []
        for item in Order.objects.filter(
                is_giveaway=False,
                date_confirmed__range=(start_date, end_date),
                reminder_email_sent=False,
        ).exclude(invoice_id__startswith='WL').order_by('-date_confirmed'):
            marker = item.owner.email
            if marker in seen: continue
            seen[marker] = 1
            if item.is_paid == False:
                items.append(item) 
        
        for item in items:
            _order_reminder_email(item.id)
        
        if items:
            _admin_cron_update(data=items, subject_line="ABANDONED BASKET emails sent today")      
                    


""" This function should do these things in order:

 1. Get a list of orders that have been abandoned within the last 3 days.
 2. Make sure that customer has not had or made any other contact with us since
 3. Send the customer a reminder and URL to continue their order.
 
 The really important thing here is to make sure we never send a reminder if:
 
  * the customer has bought something since
  * the customer has contacted us since
  * the customer has bought something before
  * 
 
"""