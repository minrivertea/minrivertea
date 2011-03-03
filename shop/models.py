from django.db import models
from django.contrib.auth.models import User
from django.contrib.sitemaps import ping_google
from django.shortcuts import get_object_or_404
import logging
from datetime import datetime

from slugify import smart_slugify
from paypal.standard.ipn.signals import payment_was_successful, payment_was_flagged
from django.template.loader import render_to_string
from django.core.mail import send_mail
from minriver import settings




# these are the categories of products on the site.
PRODUCT_CATEGORY = (
    (u'TEA', u'Tea'),
    (u'OTH', u'Other'),
    (u'POS', u'Postage'),
)

# these are the statuses of an order
ORDER_STATUS = (
    (u'1', u'Created not paid'),
    (u'2', u'Paid'),
    (u'3', u'Shipped'),
    (u'4', u'Address Problem'),
    (u'5', u'Payment flagged'),
)


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=80)		
    description = models.TextField()
    super_short_description = models.CharField(max_length=200)
    body_text = models.TextField()
    long_description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='images/product-photos')
    image_2 = models.ImageField(upload_to='images/product-photos', blank=True, null=True)
    image_2_caption = models.CharField(max_length=200, blank=True)
    image_3 = models.ImageField(upload_to='images/product-photos', blank=True, null=True)
    image_3_caption = models.CharField(max_length=200, blank=True)
    image_4 = models.ImageField(upload_to='images/product-photos', blank=True, null=True)
    image_4_caption = models.CharField(max_length=200, blank=True)
    image_5 = models.ImageField(upload_to='images/product-photos', blank=True, null=True)
    image_5_caption = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=3, choices=PRODUCT_CATEGORY)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
        
    def __unicode__(self):
        return self.name
      
    def get_absolute_url(self):
        return "/teas/%s/" % self.slug  
    
    def save(self, force_insert=False, force_update=False):
         super(Product, self).save(force_insert, force_update)
         try:
             ping_google()
         except Exception:
             # Bare 'except' because we could get a variety
             # of HTTP-related exceptions.
             pass 
 
class UniqueProduct(models.Model):
    weight = models.IntegerField(null=True, blank=True)
    weight_unit = models.CharField(help_text="Weight units", max_length=3, null=True, blank=True)
    price = models.DecimalField(help_text="Price", max_digits=8, decimal_places=2, null=True, blank=True)
    price_unit = models.CharField(help_text="Currency", max_length=3, null=True, blank=True)
    parent_product = models.ForeignKey(Product)
    available_stock = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def __unicode__(self):
        return "%s (%s%s)" % (self.parent_product, self.weight, self.weight_unit)


class Shopper(models.Model):
    user = models.ForeignKey(User)
    email = models.EmailField(blank=True, null=True)
    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    number_referred = models.IntegerField(null=True, blank=True)
    subscribed = models.BooleanField(default=True)
    slug = models.SlugField(max_length=200)
    twitter_username = models.CharField(max_length=200, blank=True, null=True)

    def __unicode__(self):
        return self.email
        
    def get_addresses(self):
        addresses = Address.objects.filter(owner=self).order_by('-id')
        return addresses 
    
    def get_orders(self):
        orders = Order.objects.filter(owner=self).order_by('-date_paid')
        return orders
    
    def get_value(self):
        value = 0
        for order in self.get_orders():
            amount = order.get_amount()
            value += amount
        
        return value
            
        
            
class Address(models.Model):
    owner = models.ForeignKey(Shopper)
    house_name_number = models.CharField(max_length=200)
    address_line_1 = models.CharField(max_length=200, blank=True, null=True)
    address_line_2 = models.CharField(max_length=200, blank=True, null=True)
    town_city = models.CharField(max_length=200)
    postcode = models.CharField(max_length=200)
    
    def __unicode__(self):
        return "%s, %s" % (self.house_name_number, self.postcode)
    
       
        
class Basket(models.Model):
    date_modified = models.DateTimeField()
    owner = models.ForeignKey(Shopper, null=True) #can delete this
    
    def __unicode__(self):
        return str(self.date_modified)
 

class BasketItem(models.Model):  
    item = models.ForeignKey(UniqueProduct)
    quantity = models.PositiveIntegerField()
    basket = models.ForeignKey(Basket)
    
    def get_price(self):
        price = self.quantity * self.item.price
        return price
        
    def __unicode__(self):
        return "%s x %s" % (self.item, self.quantity)

    
class Discount(models.Model):
    discount_code = models.CharField(max_length=40)
    name = models.CharField(max_length=200)
    discount_value = models.DecimalField(max_digits=3, decimal_places=2)
    
class Order(models.Model):
    items = models.ManyToManyField(BasketItem)
    is_confirmed_by_user = models.BooleanField(default=False)
    date_confirmed = models.DateTimeField()
    is_paid = models.BooleanField(default=False)
    date_paid = models.DateTimeField(null=True)
    address = models.ForeignKey(Address, null=True)
    owner = models.ForeignKey(Shopper)
    discount = models.ForeignKey(Discount, null=True, blank=True)
    
    STATUS_CREATED_NOT_PAID = 'created not paid'
    STATUS_PAID = 'paid'
    STATUS_SHIPPED = 'shipped'
    STATUS_ADDRESS_PROBLEM = 'address problem'
    STATUS_PAYMENT_FLAGGED = 'payment flagged'
    STATUS_CHOICES = (
            (STATUS_CREATED_NOT_PAID, u"Created, not paid"),
            (STATUS_PAID, u"Paid"),
            (STATUS_SHIPPED, u"Shipped"),
            (STATUS_ADDRESS_PROBLEM, u"Address problem"),
            (STATUS_PAYMENT_FLAGGED, u"Payment flagged"),
            
    )
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, db_index=True)
    invoice_id = models.CharField(max_length=20)
    
    def get_discount(self):
        total_price = 0
        for item in self.items:
            price = item.quantity * item.item.price
            total_price += price
        discount_amount = total_price * self.discount.discount_value
        return discount_amount
    
    def __unicode__(self):
        return self.invoice_id
    
    def get_amount(self):
        amount = 3
        for item in self.items.all():
            amount += item.get_price()
        return amount
    
    
     

class Photo(models.Model):
    shopper = models.ForeignKey(Shopper)
    photo = models.ImageField(upload_to='images/user-submitted')
    description = models.TextField(blank=True)
    published = models.BooleanField(default=False)
    published_homepage = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    related_product = models.ForeignKey(Product, blank=True, null=True)
    
    def __unicode__(self):
        return self.shopper.email
    
    def get_absolute_url(self):
        return "http://www.minrivertea.com/tea-lover/%s/" % self.shopper.slug
    
    def save(self, *args, **kwargs):
        super(Photo, self).save(*args, **kwargs)
        try:
            if self.published == True and self.email_sent == False:
                body = render_to_string('emails/new_photo_published.txt', {
                    'first_name': self.shopper.first_name,
                    'url': self.get_absolute_url(),	}    
                )
                
                subject_line = "Photo published - Min River Tea Farm" 
                email_sender = settings.SITE_EMAIL
                recipient = self.shopper.email
                send_mail(
                      subject_line, 
                      body, 
                      email_sender,
                      [recipient], 
                      fail_silently=False
                )
                
                self.email_sent = True
            else:
                pass
        except:
            return


class Referee(models.Model):
    email = models.EmailField()
    date = models.DateTimeField('date_referred', default=datetime.now)
    referred_by = models.ForeignKey(Shopper)
    
    def __unicode__(self):
        return self.email
       



# signals to connect to receipt of PayPal IPNs

def show_me_the_money(sender, **kwargs):
    ipn_obj = sender
    order = get_object_or_404(Order, invoice_id=ipn_obj.invoice)
    if order.status == Order.STATUS_PAID:
        return
        
    order.status = Order.STATUS_PAID
    order.date_paid = ipn_obj.payment_date
    order.is_paid = True
    order.save()
    
    # create and send an email to the customer
    invoice_id = order.invoice_id
    first_name = order.owner.first_name
    recipient = order.owner.email
    body = render_to_string('emails/order_confirm_customer.txt', {
    	        'first_name': first_name, 
    	        'invoice_id': invoice_id, 
    	        'order_items': order.items.all(), 
    	        'order_status': order.status})
    subject_line = "Order confirmed - Min River Tea Farm" 
    email_sender = settings.SITE_EMAIL
      
    send_mail(
                  subject_line, 
                  body, 
                  email_sender,
                  [recipient], 
                  fail_silently=False
     )
     
     # create and send an email to me
    invoice_id = order.invoice_id
    email = order.owner.email
    recipient = 'mail@minrivertea.com'
    body = render_to_string('emails/order_confirm_admin.txt', {
    	        'email': email, 
    	        'invoice_id': invoice_id, 
    	        'order_items': order.items.all(), 
    	        'order_status': order.status})
    subject_line = "NEW ORDER - %s" % invoice_id      
    email_sender = settings.SITE_EMAIL
      
    send_mail(
                  subject_line, 
                  body, 
                  email_sender,
                  [recipient], 
                  fail_silently=False
     )  
payment_was_successful.connect(show_me_the_money)    

    
def payment_flagged(sender, **kwargs):
    ipn_obj = sender
    order = get_object_or_404(Order, invoice_id=ipn_obj.invoice)
    order.status = Order.STATUS_PAYMENT_FLAGGED
    order.save()

     # create and send an email to me
    invoice_id = order.invoice_id
    email = order.owner.email
    recipient = 'mail@minrivertea.com'
    body = render_to_string('emails/order_confirm_admin.txt', {'email': email, 'invoice_id': invoice_id, 'order_items': order.items.all()})
    subject_line = "FLAGGED ORDER - %s" % invoice_id 
    email_sender = 'mail@minrivertea.com'
      
    send_mail(
                  subject_line, 
                  body, 
                  email_sender,
                  [recipient], 
                  fail_silently=False
     )   
payment_was_flagged.connect(payment_flagged)






