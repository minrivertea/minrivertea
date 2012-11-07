from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime, timedelta
import uuid


from logistics.models import WarehouseItem, CustomerPackage
from shop.models import UniqueProduct, Order, Currency

# this sends out the first 'review' email after the order was shipped.
class Command(NoArgsCommand):
    help = 'Temp to transfer stock to new logistics model'

    def handle_noargs(self, **options):

        for x in UniqueProduct.objects.filter(available_stock__gte=0, currency__code='GBP', is_active=True):
            count = x.available_stock
            print "Creating %s warehouse items for %s" % (count, x)
            while count > 0:
                new_item = WarehouseItem.objects.create(
                    hashkey=uuid.uuid1().hex,
                    unique_product=x,
                    batch='001',
                    created=datetime.now(),
                    available=datetime.now(),
                    location=WarehouseItem.UK,
                )
                
                count -= 1


                
        
     
                    

