from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sitemaps import ping_google
from django.shortcuts import get_object_or_404
import logging
from datetime import datetime, timedelta
from urlparse import urlparse

from slugify import smart_slugify
from paypal.standard.ipn.signals import payment_was_successful, payment_was_flagged
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives
from minriver import settings
from minriver.countries import COUNTRY_CHOICES


POUND = 'gbp'
DOLLAR = 'usd'
EURO = 'euro'
CURRENCY_CHOICES = (
    (POUND, u"&#163;"),
    (DOLLAR, u"&#36;"),
    (EURO, u"&#128;"),
)


class Currency(models.Model):
    code = models.CharField(max_length=5)
    symbol = models.CharField(max_length=5)
    postage_discount_threshold = models.IntegerField()
    postage_cost = models.IntegerField()
    active = models.BooleanField(default=False)
    
    
    def __unicode__(self):
        return self.code


class Product(models.Model):
    name = models.CharField(max_length=200, 
        help_text="Appears in listings and on product page if no long_name set")
    long_name = models.CharField(max_length=200, blank=True, null=True,
        help_text="Appears on the actual product page")
    slug = models.SlugField(max_length=80)
    meta_title = models.CharField(max_length=200, blank=True, null=True,
        help_text="")		
    description = models.TextField(
        help_text="The short description appearing in product listings - no HTML")
    meta_description = models.TextField(blank=True, null=True,
        help_text="")
    super_short_description = models.CharField(max_length=200)
    body_text = models.TextField()
    long_description = models.TextField(blank=True, null=True)
    extra_info = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='images/product-photos')
    image_2 = models.ImageField(upload_to='images/product-photos', blank=True, null=True)
    image_2_caption = models.CharField(max_length=200, blank=True)
    image_3 = models.ImageField(upload_to='images/product-photos', blank=True, null=True)
    image_3_caption = models.CharField(max_length=200, blank=True)
    image_4 = models.ImageField(upload_to='images/product-photos', blank=True, null=True)
    image_4_caption = models.CharField(max_length=200, blank=True)
    image_5 = models.ImageField(upload_to='images/product-photos', blank=True, null=True)
    image_5_caption = models.CharField(max_length=200, blank=True)
    category = models.ForeignKey('Category', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    list_order = models.IntegerField(null=True, blank=True)
    tag_text = models.CharField(max_length="100", blank=True, null=True)
    tag_color = models.CharField(max_length="60", blank=True, null=True,
        help_text="A Hex reference with the preceding # hash")
    coming_soon = models.BooleanField(default=False)
    recommended = models.ManyToManyField('Product', blank=True, null=True)
        
    def __unicode__(self):
        return self.name
      
    def get_absolute_url(self):
        return "/%s/%s/" % (self.category.slug, self.slug)  #important, do not change
    
    def get_lowest_price(self):
        try:
            prices = UniqueProduct.objects.filter(parent_product=self, is_sale_price=False).order_by('price')[0]
        except:
            prices = None
        return prices
    
    def get_reviews(self):
        reviews = Review.objects.filter(product=self, is_published=True)
        return reviews    
    
    def save(self, force_insert=False, force_update=False):
         super(Product, self).save(force_insert, force_update)
         try:
             ping_google()
         except Exception:
             # Bare 'except' because we could get a variety
             # of HTTP-related exceptions.
             pass 

class Category(models.Model):
    name = models.CharField(max_length=200)
    long_title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=80)
    meta_description = models.TextField(help_text="No HTML please!")
    short_description = models.TextField(help_text="Goes under the title on the page, HTML is OK.")
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return "/%s/" % self.slug

 
class UniqueProduct(models.Model):
    weight = models.IntegerField(null=True, blank=True)
    weight_unit = models.CharField(help_text="Weight units", max_length=3, null=True, blank=True)
    price = models.DecimalField(help_text="Price", max_digits=8, decimal_places=2, null=True, blank=True)
    price_unit = models.CharField(help_text="Currency", max_length=3, null=True, blank=True)
    currency = models.ForeignKey(Currency)
    parent_product = models.ForeignKey(Product)
    description = models.TextField()
    available_stock = models.IntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_sale_price = models.BooleanField(default=False)
    old_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="If it's a sale item, what was the old price?")
    
    def __unicode__(self):
        if self.weight:
            return "%s (%s%s)" % (self.parent_product, self.weight, self.weight_unit)
        else: 
            return "%s" % self.parent_product           

class Shopper(models.Model):
    user = models.ForeignKey(User)
    email = models.EmailField(blank=True, null=True)
    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    number_referred = models.IntegerField(null=True, blank=True)
    subscribed = models.BooleanField(default=False)
    slug = models.SlugField(max_length=200)
    twitter_username = models.CharField(max_length=200, blank=True, null=True)
    reminder_email_sent = models.DateTimeField(blank=True, null=True, 
        help_text="If this has a value, it means the user has received a 2 month reminder email if they didn't order for a while.")

    def __unicode__(self):
        return self.email
        
    def get_addresses(self):
        addresses = Address.objects.filter(owner=self).order_by('-id')
        return addresses 
    
    def get_orders(self):
        orders = Order.objects.filter(owner=self, is_paid=True).order_by('-date_paid')
        return orders
    
    def get_value(self):
        value = 0
        for order in self.get_orders():
            amount = order.get_amount()
            value += amount
        
        return value
            
class Review(models.Model):
    product = models.ForeignKey(Product)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    email = models.EmailField()
    text = models.TextField()
    short_text = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    is_published = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.product.name  
    
    def show_url(self):
        url = urlparse(self.url)
        return url.netloc     
            
class Address(models.Model):
    owner = models.ForeignKey(Shopper)
    house_name_number = models.CharField(max_length=200)
    address_line_1 = models.CharField(max_length=200, blank=True, null=True)
    address_line_2 = models.CharField(max_length=200, blank=True, null=True)
    town_city = models.CharField(max_length=200)
    postcode = models.CharField(max_length=200)
    country = models.CharField(max_length=200, choices=COUNTRY_CHOICES, db_index=True)
    
    def __unicode__(self):
        return "%s, %s, %s" % (self.house_name_number, self.postcode, self.country)
    
       
        
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
    is_active = models.BooleanField(default=False)
    
    
class Order(models.Model):
    items = models.ManyToManyField(BasketItem, db_index=True)
    is_confirmed_by_user = models.BooleanField(default=False)
    date_confirmed = models.DateTimeField()
    is_paid = models.BooleanField(default=False)
    is_giveaway = models.BooleanField(default=False)
    date_paid = models.DateTimeField(null=True)
    address = models.ForeignKey(Address, null=True)
    owner = models.ForeignKey(Shopper)
    discount = models.ForeignKey(Discount, null=True, blank=True)
    invoice_id = models.CharField(max_length=20)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    sampler_email_sent = models.BooleanField(default=False, 
        help_text="Has an email been sent to the order customer about a free sample?")
    sampler_sent = models.BooleanField(default=False, 
        help_text="Has a sample been sent to a friend of theirs from this order?")
    reminder_email_sent = models.BooleanField(default=False, 
        help_text="Has a 3 day reminder email been sent if the order wasn't completed?")
    review_email_sent = models.BooleanField(default=False,
        help_text="Has a friendly review email been sent (around 1 week after order is shipped)?")
    wishlist_payee = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(null=True, blank=True)
    postage_cost = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    
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
    date_shipped = models.DateTimeField(blank=True, null=True)
    
    
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
        amount = 0
        for item in self.items.all():
            amount += item.get_price()
        if amount > 50:
            pass
        else:
            amount += 3
        return amount
    
    def get_items(self):
        return self.items.all()

    def ready_to_send_review(self):
        if (self.date_paid + timedelta(days=7)) < datetime.now():
            review = True
        else:
            review = False
        return review
    
    def ready_to_send_sampler_email(self):
        if (self.date_paid + timedelta(days=14)) < datetime.now():
            sampler = True
        else:
            sampler = False
        return sampler


class Wishlist(models.Model):
    wishlist_items = models.ManyToManyField(BasketItem)
    owner = models.ForeignKey(Shopper, db_index=True)
    address = models.ForeignKey(Address)
    hashkey = models.CharField(max_length=200, blank=True, null=True)
    date_created = models.DateTimeField(default=datetime.now())
    views = models.IntegerField(default="0", blank=True, null=True)
    times_purchased = models.IntegerField(default="0", blank=True, null=True)
    
    def __unicode__(self):
        return self.owner.email
        
          
     

class Photo(models.Model):
    shopper = models.ForeignKey(Shopper)
    photo = models.ImageField(upload_to='images/user-submitted')
    published = models.BooleanField(default=False)
    published_homepage = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    related_product = models.ForeignKey(Product, blank=True, null=True)
    
    def __unicode__(self):
        return self.shopper.email
    
    def get_absolute_url(self):
        return "/tea-lover/%s/" % self.shopper.slug


class Referee(models.Model):
    email = models.EmailField()
    date = models.DateTimeField('date_referred', default=datetime.now)
    referred_by = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.email

class EmailSignup(models.Model):
    email = models.EmailField()
    date_signed_up = models.DateField()
    date_unsubscribed = models.DateField(blank=True, null=True)
    hashkey = models.CharField(max_length=256, blank=True, null=True)
    
    def __unicode__(self):
        return self.email
    
 
class EmailInstance(models.Model):
    subject_line = models.CharField(max_length=256)
    content = models.TextField()
    date_sent = models.DateTimeField(blank=True, null=True)
    
    def __unicode__(self):
        return self.subject_line   
        

class Notify(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=200, blank=True, null=True)
    product = models.ForeignKey(Product, blank=True, null=True)
    country = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateTimeField('date', default=datetime.now,
        help_text="The date that they made contact")
    email_sent = models.BooleanField(default=False, help_text="If this is ticked, don't send them emails again")

    def __unicode__(self):
        return self.email

class Page(models.Model):
    slug = models.SlugField()
    title = models.CharField(max_length=200)
    meta_title = models.CharField(max_length=200, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', blank=True, null=True)
    content = models.TextField()
    promo_image = models.ImageField(upload_to='images/learn', blank=True, null=True)
    feature_image = models.ImageField(upload_to='images/learn', blank=True, null=True)
    template = models.CharField(max_length=200, blank=True, null=True)
    right_side_boxes = models.CharField(max_length=200, blank=True, null=True)
    
    def __unicode__(self):
        return self.title
    
    def get_root(self):
        
        def _iterator(obj):
            if obj.parent:
                return _iterator(obj.parent)
            else:
                return obj
        
        return _iterator(self)
        
    
    def get_nav_tree(self):
        if self.parent is None: 
            nav_items = Page.objects.filter(parent=self)
        else:
            if self.parent.parent is None:
                nav_items = Page.objects.filter(parent=self.parent)
            else:
                if self.parent.parent.parent is None:
                    nav_items = Page.objects.filter(parent=self.parent.parent)
                else:
                    if self.parent.parent.parent.parent is None:
                        nav_items = Page.objects.filter(parent=self.parent.parent.parent)
        return nav_items
    
    def get_children(self):
        items = Page.objects.filter(parent=self)
        return items
    
    def get_absolute_url(self):
        url = "/%s/" % self.slug  
        return url

    def get_products_mentioned(self):
        teas = Product.objects.filter(is_active=True)
        products = []
        for tea in teas:
            if tea.name in self.content:
                products.append(tea)
        return products
        
        

# signals to connect to receipt of PayPal IPNs

def show_me_the_money(sender, **kwargs):
    ipn_obj = sender
    order = get_object_or_404(Order, invoice_id=ipn_obj.invoice)
    
    # this prevents double emails being sent...
    if order.status == Order.STATUS_PAID:
        return
    
    order.status = Order.STATUS_PAID
    order.date_paid = ipn_obj.payment_date
    order.is_paid = True
    order.save()
    
    # if it was a WISHLIST payment...
    if order.wishlist_payee:
        # get the owner's wishlist (remember, they can only have 1 wishlist)
        wishlist = get_object_or_404(Wishlist, owner=order.owner)
        for item in order.items.all():
            try:
                # remove all the paid items from the wishlist
                wishlist.wishlist_items.remove(item)
            except:
                pass
        
        wishlist.save()     
    from minriver.shop.emails import _payment_success_email 
    _payment_success_email(order)
    
payment_was_successful.connect(show_me_the_money)    

    
def payment_flagged(sender, **kwargs):
    ipn_obj = sender
    order = get_object_or_404(Order, invoice_id=ipn_obj.invoice)
    
    # this prevents double emails being sent...
    if order.status == Order.STATUS_PAYMENT_FLAGGED:
        return
    
    order.status = Order.STATUS_PAYMENT_FLAGGED
    order.save()

    from minriver.shop.emails import _payment_flagged_email
    _payment_flagged_email(request, order)

payment_was_flagged.connect(payment_flagged)






