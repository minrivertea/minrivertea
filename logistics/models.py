from django.db import models
from datetime import datetime, timedelta
import uuid

from shop.models import UniqueProduct, Order, Currency



class WarehouseItem(models.Model):
    hashkey = models.CharField(max_length=100, help_text='Type "LAZY" if you want the system to auto-generate a key.')
    unique_product = models.ForeignKey(UniqueProduct)
    batch = models.CharField(max_length=10)
    package = models.ForeignKey('CustomerPackage', blank=True, null=True) 
    
    # DATES
    produced = models.DateTimeField(blank=True, null=True, 
        help_text="When was the item produced? Really only relevant for tea or perishables.")
    created = models.DateTimeField(default=datetime.now(), help_text="When did the item enter our stock system?")
    available = models.DateTimeField(blank=True, null=True, help_text="When was the item available to sell?")
    sold = models.DateTimeField(blank=True, null=True, help_text="When was the item sold?")
    
        
    SOLD = 'sold'
    DESTROYED = 'destroyed'
    GIVEAWAY = 'giveaway'
    LOST = 'lost'
    REMOVALS = (
        (SOLD, u"Sold"),
        (DESTROYED, u"Destroyed"),
        (LOST, u"Lost"),
        (GIVEAWAY, u"Giveaway"),
    )
    
    reason = models.CharField(max_length=20, choices=REMOVALS, blank=True, null=True)
    
    CHINA = 'china'
    UK = 'uk'
    LOCATIONS = (
        (CHINA, u"China"),
        (UK, u"United Kingdom"), 
    )
    
    location = models.CharField(max_length=10, choices=LOCATIONS)
    
    def __unicode__(self):
        return self.hashkey
        
    def save(self, *args, **kwargs):
        if self.hashkey == 'LAZY':
            self.hashkey = uuid.uuid1().hex
        super(WarehouseItem, self).save(*args, **kwargs) # Call the "real" save() method.
    
    def months_old(self):
        
        if (self.produced + timedelta(weeks=52)) <= datetime.now():
            return 12
        
        if (self.produced + timedelta(weeks=26)) <= datetime.now():
            return 6
            
        return False
            



class CustomerPackage(models.Model):
    order = models.ForeignKey(Order)
    created = models.DateTimeField(default=datetime.now())
    is_preorder = models.BooleanField(default=False)
    shipping_due_date = models.DateField(blank=True, null=True, help_text="Only used for monthly order packages")
    posted = models.DateTimeField(blank=True, null=True)
    postage_cost = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    postage_currency = models.ForeignKey(Currency, null=True, blank=True)
    
    
    # EMAILS RELATED TO THE ORDER
    shipped_email_sent = models.DateTimeField(blank=True, null=True)
    brewing_tips_email_sent = models.DateTimeField(blank=True, null=True)
    review_email_sent = models.DateTimeField(blank=True, null=True)
    reorder_email_sent = models.DateTimeField(blank=True, null=True)
    
    
    def __unicode__(self):
        return "%s : %s" % (self.order, self.order.owner)    
    
    def get_items(self):
        items = WarehouseItem.objects.filter(package=self)
        return items
    
    def repeat_order(self):
        if CustomerPackage.objects.filter(order=self.order).count() > 1:
            return True
        else:
            return False
    
    def repeat_order_first(self):
        try:
            first = CustomerPackage.objects.filter(order=self.order)[0]
        except:
            return False
        
        if first.id == self.id:
            return True
     
    def repeat_order_last(self):
        try:
            last = CustomerPackage.objects.filter(order=self.order).order_by('-created')[0]
        except:
            return False
        
        if last.id == self.id:
            return True