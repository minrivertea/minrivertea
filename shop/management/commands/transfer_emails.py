from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime, timedelta
import uuid

from emailer.models import Subscriber
from shop.models import EmailSignup, Shopper


class Command(NoArgsCommand):
    help = 'Temp to transfer stock to new logistics model'

    def handle_noargs(self, **options):

        for x in EmailSignup.objects.all():
            
            # check no duplicates
            if Subscriber.objects.filter(email=x.email).count() > 0:
                print "skipping, duplicate of %s" % x.email
            else:
                new_object = Subscriber.objects.create(
                    email=x.email,
                    date_signed_up=x.date_signed_up,
                    language='en',
                    date_unsubscribed=x.date_unsubscribed,
                    confirmed=True,
                )
                print "Added new email subscription object for : %s" % x.email
        
        
        for y in Shopper.objects.filter():
            
            # check no duplicates
            if Subscriber.objects.filter(email=y.email).count() > 0:
                print "skipping, duplicate of %s" % y.email
            else:
                new_object = Subscriber.objects.create(
                    email=y.email,
                    date_signed_up=datetime.now(),
                    language='en',
                    confirmed=True,
                )
                
                if y.subscribed == False:
                    new_object.date_unsubscribed = datetime.now()
                    new_object.save()
                
                print "Added new email subscription object for : %s" % y.email
                
        
     
                    

