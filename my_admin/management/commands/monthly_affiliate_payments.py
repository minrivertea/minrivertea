from django.conf import settings
from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime, timedelta
from django.core.mail import EmailMessage

import csv
import StringIO
import calendar

# import various bits and pieces
from shop.models import Order
from emailer.views import order_reminder_email, _admin_cron_update
from datetime import datetime, timedelta, date
from django.db.models import Q

def subtract_one_month(t):
    """Return a `datetime.date` or `datetime.datetime` (as given) that is
    one month later.
    
    Note that the resultant day of the month might change if the following
    month has fewer days:
    
        >>> subtract_one_month(datetime.date(2010, 3, 31))
        datetime.date(2010, 2, 28)
    """
    one_day = timedelta(days=1)
    one_month_earlier = t - one_day
    while one_month_earlier.month == t.month or one_month_earlier.day > t.day:
        one_month_earlier -= one_day
    return one_month_earlier


class Command(NoArgsCommand):
    help = 'Generates a monthly report of Affiliate sales and then emails to affiliate people.'

    def handle_noargs(self, **options):
        
        start_date = subtract_one_month(datetime.now())
        end_date = datetime.now()
        
        
        # get a list of all the sales this month that are affiliates
        orders = Order.objects.filter(
            date_paid__isnull=False, 
            status=Order.STATUS_PAID, 
            affiliate_referrer__isnull=False,
            date_paid__range=(start_date, end_date),
            # ADD DATE RANGE
        )  
        
        # create a CSV file with details of all the orders
        output = StringIO.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Order ID', 'Affiliate Referrer', 'Date', 'Amount', 'Currency'])
        for o in orders:
            writer.writerow([o.invoice_id, o.affiliate_referrer, o.date_paid, o.get_amount_eur(), 'EUR'])
        
        filename = '%s-%s-%s-minrivertea-affiliate-payments.csv' % (start_date.year, start_date.month, start_date.day)
        
        email = EmailMessage('Monthly Affiliate Payments', '', settings.SITE_EMAIL, ['chris@minrivertea.com'])
        email.attach(filename, writer, 'text/csv')
        email.send()

        # send CSV file by email to me  
                    


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