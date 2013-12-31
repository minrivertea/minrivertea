from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime, timedelta

# import various bits and pieces
from shop.models import Order, Product, Page, Currency
from logistics.models import CustomerPackage, WarehouseItem
from datetime import datetime, timedelta
from django.db.models import Q
from django.utils.translation import ugettext as _


class Command(NoArgsCommand):

    def handle_noargs(self, **options):
        
        for c in CustomerPackage.objects.all():
            
            print c.order.id
            
            try:
                currency = Currency.objects.get(code=c.order.final_currency_code)
            except:
                currency = Currency.objects.get(code='GBP')

                
            # THIS STUFF UPDATES THE CUSTOMER PACKAGES THEMSELVES
            if c.order.discount:
                c.discount_amount = c.order.get_discount()
                print "  DISCOUNT: %s" % c.discount_amount 
            
            amount = 0
            for item in c.order.items.all():
                amount += item.get_price()
                
            if amount > currency.postage_discount_threshold:
                c.postage_paid = 0
            else:
                c.postage_paid = currency.postage_cost
                
            print "  POSTAGE: %s" % c.postage_paid
            c.save()                        
            
            print "  ITEMS" 
            # NOW LET'S UPDATE THE WAREHOUSE ITEM PRICES
            for x in c.get_items():
                
                for o in c.order.items.filter(item__parent_product=x.unique_product.parent_product):
                    
                    if x.unique_product.weight == o.item.weight and currency == o.item.currency:
                        x.list_price = o.item.price
                        x.sale_currency = o.item.currency
                        x.sale_price = o.item.get_price()
                    
                    if x.unique_product.weight == None and currency == o.item.currency:
                        x.list_price = o.item.price
                        x.sale_currency = o.item.currency
                        x.sale_price = o.item.get_price()
                    
                    x.save()

                
                print "    %s" % x.unique_product
                print "       %s%s" % (x.sale_price, x.sale_currency)

            
            
            