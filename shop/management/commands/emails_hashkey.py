from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime, timedelta
import uuid

from emailer.models import Subscriber


class Command(NoArgsCommand):
    help = 'Temp to transfer stock to new logistics model'

    def handle_noargs(self, **options):

        for x in Subscriber.objects.all():
            
            x.hashkey = uuid.uuid1().hex
            x.save()
            print "changed %s" % x.email                    

