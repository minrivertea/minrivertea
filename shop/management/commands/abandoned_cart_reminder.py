from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime, timedelta

# import various bits and pieces
from shop.models import Order, Review
from emailer.views import abandoned_basket, _admin_cron_update
from datetime import datetime, timedelta
from django.db.models import Q

# this sends out the first 'review' email after the order was shipped.
class Command(NoArgsCommand):
    help = 'Sends emails to people who have abandoned their cart in the last day.'

    def handle_noargs(self, **options):
        
        # SET A DATE RANGE OF 1 DAY
        start_date = (datetime.now() - timedelta(days=1)) 
        end_date = datetime.now() # now
        
        
        seen = {}
        items = []
        
        # MAKE A LIST OF ORDERS THAT WERE MADE IN THE LAST DAY
        orders = Order.objects.filter(
                date_confirmed__range=(start_date, end_date),
            ).order_by('-date_confirmed')

        # UNIQUE-IFY THE LIST AGAINST EMAIL ADDRESS SO WE ONLY HAVE THE MOST RECENT ONE
        for o in orders:
            marker = o.owner.email
            if marker in seen: continue
            seen[marker] = 1
            items.append(o) 
         
        # IF THE MOST RECENT ONE ISN'T PAID OR HASN'T RECEIVED AN EMAIL YET, THEN SEND THEM THE EMAIL
        for i in items:
            if not i.date_paid and i.reminder_email_sent == False:
                abandoned_basket(i.id)
                i.reminder_email_sent = True
                i.save()
        
        
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