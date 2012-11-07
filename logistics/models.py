from django.db import models
from datetime import datetime, timedelta

from shop.models import UniqueProduct, Order, Currency



class WarehouseItem(models.Model):
    hashkey = models.CharField(max_length=100)
    unique_product = models.ForeignKey(UniqueProduct)
    batch = models.CharField(max_length=10) 
    
    created = models.DateTimeField(default=datetime.now())
    available = models.DateTimeField(blank=True, null=True)
    sold = models.DateTimeField(blank=True, null=True)
    
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



class CustomerPackage(models.Model):
    order = models.ForeignKey(Order)
    items = models.ManyToManyField(WarehouseItem, blank=True, null=True)
    created = models.DateTimeField(default=datetime.now())
    posted = models.DateTimeField(blank=True, null=True)
    postage_cost = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    postage_currency = models.ForeignKey(Currency, null=True, blank=True)
    
    def __unicode__(self):
        return "%s : %s" % (self.order, self.order.owner)
    
    