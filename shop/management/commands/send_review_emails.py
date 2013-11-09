from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime, timedelta

from logistics.models import CustomerPackage
from emailer.views import product_review, _admin_cron_update


class Command(NoArgsCommand):
    help = 'Sends out review emails to customers who should have received their tea by now'

    def handle_noargs(self, **options):
        
        # GET ALL CUSTOMER PACKAGES THAT HAVE BEEN SHIPPED BETWEEN 
        # 2-4 WEEKS AGO AND HAVEN'T RECEIVED A REVIEW EMAIL YET
        items = []
        two_weeks = (datetime.now() - timedelta(days=14))        
        four_weeks = (datetime.now() - timedelta(days=28))
        for package in CustomerPackage.objects.filter(
            posted__range=(four_weeks, two_weeks),
            review_email_sent__isnull=True,
        ):
             
            # SEND THE EMAIL AND UPDATE THE PACKAGE 
            product_review(package.order.id)
            package.review_email_sent = datetime.now()
            package.save()
            items.append(package)
        
        # SEND A LIST OF REVIEW EMAILS SENT TO ADMIN
        if items:
            _admin_cron_update(data=items, subject_line="REVIEW emails sent today")      
                    


""" This function should do these things in order:

 1. Get a list of customer packages that have been shipped, where no review email has been sent to the customer
 2. Check if the shipping date is more than 14 days before
 3. Send the customer an email asking for a review
 4. Send the admin user a list of the emails sent
 
"""