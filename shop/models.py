from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sitemaps import ping_google
from django.shortcuts import get_object_or_404
import logging
from datetime import datetime, timedelta
from urlparse import urlparse
from django.utils import translation
from django.core.urlresolvers import reverse
from django.contrib.sites.models import Site



from slugify import smart_slugify
from paypal.standard.ipn.signals import payment_was_successful, payment_was_flagged
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives
from countries import COUNTRY_CHOICES

from ckeditor.fields import RichTextField


GREEN = '#177117'
BLUE = '#1f7dc5'
PINK = '#eb68a0'
RED = '#d51515'
TAG_COLORS = (
    (GREEN, u'Green'),
    (PINK, u'Pink'),
    (BLUE, u'Blue'),
    (RED, u'Red'),
)


GLOBAL = 'global'
CHINA = 'china'
SITES = (
    (GLOBAL, u'Global'),
    (CHINA, u'China'),
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
        help_text="A longer and more descriptive title that might appear in Google's search results")		
    description = models.TextField(
        help_text="The short description appearing in product listings - no HTML")
    meta_description = models.TextField(blank=True, null=True,
        help_text="Customized search description that might appear in Google's search results")
    super_short_description = models.CharField(max_length=200,
        help_text="Appears as the really short description in right-box product listings")
    body_text = models.TextField(
        help_text="The introduction paragraph at the top-right of the main product page")
    long_description = RichTextField(blank=True, null=True)
    extra_info = models.TextField(blank=True, null=True,
        help_text="This is normally the 'tasting notes' section. Add an 'h3' as the title.")
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
    tag_color = models.CharField(max_length="60", blank=True, null=True, choices=TAG_COLORS,
        help_text="A Hex reference with the preceding # hash")
    
    map_image = models.ImageField(upload_to='images/maps', blank=True, null=True)
    map_caption = models.CharField(max_length=200, blank=True, null=True)
    
    farm_image = models.ImageField(upload_to='images/product-photos', blank=True, null=True)
    farm_caption = models.CharField(max_length=200, blank=True, null=True)
    
    # for the tea brewing
    brew_time = models.IntegerField(blank=True, null=True,
        help_text="Give time in seconds")
    brew_weight = models.IntegerField(blank=True, null=True,
        help_text="The amount to use per brew in grams")
    brew_temp = models.IntegerField(blank=True, null=True,
        help_text="The temperature of water to use in degrees celsius")
    
        
    def __unicode__(self):
        return self.name
    
    def get_preorder_date(self):
        date = (datetime.today() + timedelta(days=22))
        return date
    
    def get_absolute_url(self):
        return reverse('finder', args=[self.category.slug, self.slug])
    
    def get_url_by_id(self):
        url = reverse('product_by_id', args=[self.id])
        return url

    def get_lowest_price(self, currency, exclude_sales=False):
        try:
            if exclude_sales == True:
                price = UniqueProduct.objects.filter(
                    parent_product=self,
                    is_active=True, 
                    currency=currency,
                    is_sale_price=False,
                ).order_by('price')[0]
            else:
                price = UniqueProduct.objects.filter(
                    parent_product=self,
                    is_active=True, 
                    currency=currency,
                ).order_by('price')[0]
        except:
            price = None
        return price
    
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
    parent_category = models.ForeignKey('self', blank=True, null=True)
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('finder', args=[self.slug])

    def get_url_by_id(self):
        url = reverse('category_by_id', args=[self.id])
        return url
    
    def get_sub_categories(self):
        subs = Category.objects.filter(parent_category=self)
        return subs
    
    def get_products(self):
        from shop.views import _get_products
        return _get_products(cat=self.slug)

 
class UniqueProduct(models.Model):
    weight = models.IntegerField(null=True, blank=True)
    weight_unit = models.CharField(help_text="Weight units", max_length=3, null=True, blank=True)
    price = models.DecimalField(help_text="Price", max_digits=8, decimal_places=2, null=True, blank=True)
    currency = models.ForeignKey(Currency)
    parent_product = models.ForeignKey(Product)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_sale_price = models.BooleanField(default=False)
    old_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True,
        help_text="If it's a sale item, what was the old price?")
    
    def __unicode__(self):
        if self.weight:
            return "%s (%s%s)" % (self.parent_product, self.weight, self.weight_unit)
        else: 
            return "%s" % self.parent_product  
    
    def stocks(self):
        from logistics.models import WarehouseItem
        # how many items match this product, this weight, and are in the UK, and not sold?
        stocks = WarehouseItem.objects.filter(
            unique_product__parent_product=self.parent_product, 
            unique_product__weight=self.weight,
            sold__isnull=True, 
            location=WarehouseItem.UK,
            unique_product__currency__code='GBP')
        if len(stocks) > 0:
            return stocks 
        else:
            return None
    
    def get_saving(self):
        if self.is_sale_price:
            return (self.old_price - self.price)
        else:
            return None       

class Shopper(models.Model):
    user = models.ForeignKey(User)
    # TODO - get rid of this duplication of Shopper/User email, lastname and firstname
    email = models.EmailField(blank=True, null=True)
    first_name = models.CharField(max_length=200, null=True, blank=True)
    last_name = models.CharField(max_length=200, null=True, blank=True)
    language = models.CharField(max_length=20, choices=settings.LANGUAGES, default='en')
    number_referred = models.IntegerField(null=True, blank=True)
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
    last_name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    text = models.TextField()
    short_text = models.TextField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    is_published = models.BooleanField(default=False)
    date_submitted = models.DateTimeField(blank=True, null=True)
    lang = models.CharField(max_length=5, choices=settings.LANGUAGES)
    
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
    province_state = models.CharField(max_length=200, blank=True, null=True)
    postcode = models.CharField(max_length=200)
    country = models.CharField(max_length=200, choices=COUNTRY_CHOICES, db_index=True)
    phone = models.CharField(max_length=80, blank=True, null=True)
    
    def __unicode__(self):
        return "%s, %s, %s" % (self.house_name_number, self.postcode, self.country)
    
       
        
class Basket(models.Model):
    date_modified = models.DateTimeField()
    owner = models.ForeignKey(Shopper, null=True) # DELETE
    
    def __unicode__(self):
        return str(self.date_modified)
 

class BasketItem(models.Model):  
    item = models.ForeignKey(UniqueProduct)
    quantity = models.PositiveIntegerField()
    basket = models.ForeignKey(Basket)
    
    # specific for monthly ordering
    monthly_order = models.BooleanField()
    months = models.IntegerField(blank=True, null=True)
    
    def get_price(self):
        if self.monthly_order:
            from utils import _get_monthly_price
            price = _get_monthly_price(self.item, self.months)
        else:
            price = self.item.price
            
        total = self.quantity * price
        return total
        
        
    def __unicode__(self):
        if self.monthly_order:
            return "%s x %s (%s months)" % (self.item, self.quantity, self.months)
        else:
            return "%s x %s" % (self.item, self.quantity)

    
class Discount(models.Model):
    discount_code = models.CharField(max_length=40)
    name = models.CharField(max_length=200)
    discount_value = models.DecimalField(max_digits=3, decimal_places=2,
        help_text="A decimal expressing the amount of discount. Eg. 0.2 = 20% off.")
    single_use = models.BooleanField(default=True)
    expiry_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.name
    
    
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
    wishlist_payee = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(null=True, blank=True)
    affiliate_referrer = models.CharField(max_length=200, blank=True, null=True, 
        help_text="A referrer ID from the affiliate scheme should be stored here.")
    
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
    
    # THESE WILL STORE THE FINAL INFORMATION ONCE THE ORDER IS SOLD
    final_amount_paid = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=2)
    final_discount_amount = models.DecimalField(blank=True, null=True, max_digits=8, decimal_places=2)
    final_currency_code = models.CharField(max_length=3, blank=True, null=True)
    final_items_list = models.TextField(blank=True, null=True)
    
    
    def get_discount(self):
        total_price = 0
        for item in self.items:
            price = item.quantity * item.item.price
            total_price += price
        discount_amount = total_price * self.discount.discount_value
        return discount_amount
    
    def __unicode__(self):
        return self.invoice_id
    
    
    def get_paypal_ipn(self):
        from paypal.standard.ipn.models import PayPalIPN
        try:
            ipn = PayPalIPN.objects.filter(invoice=self.invoice_id)[0]
        except:
            ipn = None
        return ipn
    
    def get_amount(self, no_discount=False, convert=None):
        

        currency = self.get_currency()
        if currency == None:
            currency = get_object_or_404(Currency, code='GBP')
        
        amount = 0
        for item in self.items.all():
            amount += item.get_price()
            
        if amount > currency.postage_discount_threshold:
            pass
        else:
            amount += currency.postage_cost
        
        if no_discount == False:
            if self.discount:
                discount_amount = amount * self.discount.discount_value
                amount -= discount_amount
        
        if convert:
            # this is so we can convert it into EUR for the affiliate scheme
            if currency.code == 'GBP':
                amount = float(amount) * float(1.18)
            
            if currency.code == 'USD':
                amount = float(amount) * float(0.7778)
                
            if currency.code == 'EUR':
                pass

        return amount
    
    def get_amount_pre_discount(self):
        return self.get_amount(no_discount=True)
    
    # THIS IS FOR THE AFFILIATE SCHEME, THEY REQUIRE EURO AMOUNTS
    def get_amount_eur(self):
        return self.get_amount(convert='EUR')
    
    def get_currency(self):
        try:
            item = self.items.all()[0]
            curr = item.item.currency
        except:
            curr = None
        return curr
    
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
        


class Page(models.Model):
    slug = models.SlugField(max_length=100)
    title = models.CharField(max_length=200)
    meta_title = models.CharField(max_length=200, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', blank=True, null=True)
    content = RichTextField()
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
        
        def _iterator(obj):
            if obj.parent:
                return _iterator(obj.parent)
            else:
                return obj
        
        root = None
        level_one = None
        level_two = None
        level_three = None
        pages = Page.objects.all()
        
        root = _iterator(self) # THE ABSOLUTE ROOT OF THE CURRENT PAGE
        all_level_one = pages.filter(parent=root) # POPULATES THE MAIN SUBNAV
        all_level_two = pages.filter(parent__parent=root)
        all_level_three = pages.filter(parent__parent__parent=root)
        
        
        # IS THIS PAGE THE ROOT?
        if self == root:
            pass
        
        # IS THIS A 1ST LEVEL PAGE
        if self in all_level_one:
            level_two = self.get_children()
        
        
        # IS THIS A 2ND LEVEL PAGE?
        if self in all_level_two:
            level_two = pages.filter(parent=self.parent)
            level_three = self.get_children()
        
        
        # IS THIS A 3RD LEVEL PAGE?
        if self in all_level_three:
            level_two = pages.filter(parent=self.parent.parent)
            level_three = pages.filter(parent=self.parent)
            level_four = self.get_children()
                                
        
            
        result = {'root': root, 'one': all_level_one, 'two': level_two, 'three': level_three}
        return result
    
    def get_breadcrumb(self):
        
        items = []
        def _iterator(obj):
            items.insert(0, obj)
            if obj.parent:
                _iterator(obj.parent)
            
            return items
        
        return _iterator(self)
            
    
    def get_children(self):
        items = Page.objects.filter(parent=self)
        return items
    
    def get_absolute_url(self):
        url = reverse('page', args=[self.slug]) 
        return url
    
    def get_url_by_id(self):
        url = reverse('page_by_id', args=[self.id])
        return url
        

# signals to connect to receipt of PayPal IPNs
def show_me_the_money(sender, **kwargs):
    ipn_obj = sender
    order = get_object_or_404(Order, invoice_id=ipn_obj.invoice)
    
    # PREVENTS DUPLICATES
    if order.status == Order.STATUS_PAID:
        return
    
    # SEND THE EMAILS FIRST !IMPORTANT!
    from emailer.views import _payment_success_email 
    _payment_success_email(order)
    
    # NOW CREATE A CUSTOMER PACKAGE
    from logistics.models import CustomerPackage
    if CustomerPackage.objects.filter(order=order).count() == 0: # PREVENTS DUPLICATES
        from logistics.views import _create_customer_package
        _create_customer_package(order)
    
    
    # UPDATE THE ORDER DETAILS
    order.status = Order.STATUS_PAID
    order.date_paid = ipn_obj.payment_date
    order.is_paid = True
    
    # UPDATE ORDER FINAL PAYMENT INFO
    order.final_amount_paid = ipn_obj.mc_gross
    if order.get_amount_pre_discount() != ipn_obj.mc_gross:
        order.final_discount_amount = order.get_amount_pre_discount() - ipn_obj.mc_gross
    
    try:    
        item_list = ''
        for item in order.items.all():
            item_list.join((item_list, str(item), '\n'))
            
        order.final_items_list = item_list
    except:
        pass
        
    order.final_currency_code = ipn_obj.mc_currency
    order.save()
    
    # IF THERE WAS A SINGLE USE DISCOUNT, UPDATE IT
    if order.discount:
        if order.discount.single_use == True:
            order.discount.is_active = False
            order.discount.save()
    
    # DELETE THE NOW OBSOLETE BASKET ITEMS ASSOCIATED WITH THIS ORDER
    #for item in order.items.all():
    #    item.delete()
    
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
        
payment_was_successful.connect(show_me_the_money)    

    
def payment_flagged(sender, **kwargs):
    ipn_obj = sender
    order = get_object_or_404(Order, invoice_id=ipn_obj.invoice)
    
    # PREVENTS DUPLICATES
    if order.status == Order.STATUS_PAYMENT_FLAGGED or order.status == Order.STATUS_PAID:
        return
    
    order.status = Order.STATUS_PAYMENT_FLAGGED
    order.date_paid = ipn_obj.payment_date
    order.is_paid = True
    order.save()

    from logistics.models import CustomerPackage
    if CustomerPackage.objects.filter(order=order).count() == 0: # PREVENTS DUPLICATES
        from logistics.views import _create_customer_package
        _create_customer_package(order)

    from emailer.views import _payment_flagged_email
    _payment_flagged_email(order)

payment_was_flagged.connect(payment_flagged)






