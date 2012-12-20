from django.db import models
from datetime import datetime, timedelta
import uuid

from shop.models import UniqueProduct, Order, Currency



class WarehouseItem(models.Model):
    hashkey = models.CharField(max_length=100, help='Type "LAZY" if you want the system to auto-generate a key.')
    unique_product = models.ForeignKey(UniqueProduct)
    batch = models.CharField(max_length=10) 
    
    created = models.DateTimeField(default=datetime.now(), help_text="The date the item entered the stock system")
    available = models.DateTimeField(blank=True, null=True, help_text="The date the item was made available to ship")
    sold = models.DateTimeField(blank=True, null=True)
    package = models.ForeignKey('CustomerPackage', blank=True, null=True)
        
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



class CustomerPackage(models.Model):
    order = models.ForeignKey(Order)
    items = models.ManyToManyField(WarehouseItem, blank=True, null=True)
    created = models.DateTimeField(default=datetime.now())
    is_preorder = models.BooleanField(default=False)
    posted = models.DateTimeField(blank=True, null=True)
    postage_cost = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    postage_currency = models.ForeignKey(Currency, null=True, blank=True)
    
    def __unicode__(self):
        return "%s : %s" % (self.order, self.order.owner)    
    
    def get_items(self):
        items = WarehouseItem.objects.filter(package=self)
        return items