from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime, timedelta
import uuid


from logistics.models import WarehouseItem, CustomerPackage
from shop.models import UniqueProduct, Order, Currency

# this sends out the first 'review' email after the order was shipped.
class Command(NoArgsCommand):
    help = 'Temp to transfer stock to new logistics model'

    def handle_noargs(self, **options):

        # NOW WE WILL CREATE THE PAST ORDERS, MAKING ALREADY COMPLETED WAREHOUSE ITEMS AND CUSTOMER PACKAGES        
        for x in Order.objects.filter(is_paid=True):

            date_created = x.date_shipped
            if date_created == None:
                date_created = x.date_paid
            
            if date_created == None:
                date_created = x.date_confirmed
            
            
            # CREATE A CUSTOMER PACKAGE FIRST
            package = CustomerPackage.objects.create(
                order=x,
                created=x.date_confirmed,
            )
            
            print "Created new package for %s" % x
            
            
            # NOW WE'LL CREATE COMPLETED WAREHOUSE ITEMS FOR EACH OF THE ORDER ITEMS.
            for i in x.items.all():
                print "   adding %s to package" % i
                new_item = WarehouseItem.objects.create(
                    hashkey=uuid.uuid1().hex,
                    unique_product=i.item,
                    batch='001',
                    created=x.date_confirmed,
                    available=x.date_confirmed,
                    location=WarehouseItem.UK,
                )
                
                
                if x.is_giveaway:
                    new_item.reason = WarehouseItem.GIVEAWAY
                    new_item.sold = x.date_confirmed
                else:
                    new_item.reason = WarehouseItem.SOLD
                    new_item.sold = x.date_paid
                
                new_item.save()

                package.items.add(new_item)
            
            if x.status == Order.STATUS_SHIPPED:
                if x.date_shipped == None:
                    package.posted = x.date_paid
                else:
                    package.posted = x.date_shipped
                    
                package.postage_cost = x.postage_cost
                package.postage_currency = Currency.objects.get(code='GBP')
            
            
            package.save()
            
            
                
            
            
            
                
        
     
                    

