from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime, timedelta

# import various bits and pieces
from logistics.models import CustomerPackage, WarehouseItem

# this is the function for deleting all basketitems not needed, and all baskets over 2 months old.
class Command(NoArgsCommand):
    help = 'Changes relationship models of CP and WHI in logistics app'

    def handle_noargs(self, **options):

        for c in CustomerPackage.objects.all():
            for x in c.items.all():
                if x.package:
                    print "Problem with package %s and warehouse item %s" % (c, x)
                    print "    this item is already owned by %s" % x.package
                    pass
                else:
                    x.package = c
                    x.save()
                
                # x.package = None
                # x.save()

