from django.core.management.base import NoArgsCommand, CommandError
from datetime import datetime, timedelta

from logistics.models import CustomerPackage
from shop.models import Order, Shopper, Product, UniqueProduct
from emailer.views import _send_two_month_reminder_email, _admin_cron_update


class Command(NoArgsCommand):
    help = "Updates old orders with text version of items"

    def handle_noargs(self, **options):        
        
        for c in CustomerPackage.objects.filter(order__is_paid=True):
            o = c.order
                        
            # UPDATE THE FINAL ITEMS LIST
            items_list = ''
            for x in o.items.all():                
                items_list += "%s, %s%s, %s, %s \n" % (
                    x.item.parent_product, 
                    x.item.weight, 
                    x.item.weight_unit, 
                    x.quantity, 
                    x.item.price,
                )
            o.final_items_list = items_list

            # UPDATE THE FINAL CURRENCY
            try:
                o.final_currency_code = o.get_currency().code
            except:
                o.final_currency_code = 'GBP'
            
            # UPDATE THE FINAL AMOUNT PAID
            try:
                o.final_amount_paid = o.get_paypal_ipn().mc_gross
            except:
                pass
            
            # UPDATE ANY DISCOUNT
            o.final_discount_amount = o.get_discount()                

            # FINALLY SAVE THE ITEM
            o.save()
        