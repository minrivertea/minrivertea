from django.core.management.base import NoArgsCommand, CommandError

from emailer.views import _send_email
from shop.models import Product, NotifyOutOfStock, UniqueProduct, Discount
from random import randint

from datetime import datetime, timedelta


class Command(NoArgsCommand):
    help = 'Sends out emails to anyone who requested notification when something comes back in stock.'

    def handle_noargs(self, **options):

        # FIND ALL OF THE NOTIFICATIONS FIRST
        notifications = NotifyOutOfStock.objects.all()
        
        # NOW LET'S SEE IF ANY OF THOSE PRODUCTS ARE IN STOCK
        for n in notifications:
            
            print n
            
            product = n.product
            unique_products = UniqueProduct.objects.filter(
                    parent_product=product,
                    currency__code='GBP',
                    is_active=True,
            )
            
            for u in unique_products:
                
                
                if u.stocks().available:
                                    
                    try:
                        
                        # MAKE A DISCOUNT CODE
                        discount = Discount.objects.create(
                            discount_code=randint(10000, 99999),
                            name=n.email,
                            discount_value=0.05,
                            expiry_date=(datetime.now() + timedelta(days=7)),
                            is_active=True,
                        )
            
            
                        # SEND AN EMAIL 
                        subject_line = "%s - back in stock at minrivertea.com" % product.name
                        template = 'shop/emails/out_of_stock_notification.txt'
                        
                        _send_email(
                                n.email, 
                                subject_line, 
                                template, 
                                extra_context={'product': product, 'discount_code': discount.discount_code}, 
                        )                    
                        
                        # DELETE THE NOTIFICATION
                        n.delete()
                        
                        
                    except:
                        pass
                    
                    
                    # SKIP TO THE NEXT NOTIFICATION 
                    continue
        
        
       
