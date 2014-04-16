# DJANGO CORE
from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from django.template import RequestContext
from paypal.standard.forms import PayPalPaymentsForm
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import ugettext as _
from django.utils.translation import get_language
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Q

# PYTHON
import urllib
import urllib2
import xml.etree.ElementTree as etree
from django.utils import simplejson
from itertools import chain

from PIL import Image
from cStringIO import StringIO
import os
import datetime
from datetime import timedelta
import uuid
import re
import stripe

# APP
from shop.models import *
from blog.models import BlogEntry
from shop.utils import _render, _get_basket, _get_currency, _get_country, _get_region, \
    _changelang, _set_currency, _get_products, _get_monthly_price, weight_converter, _get_basket_value,  secure_required
from shop.forms import *
from slugify import smart_slugify


class BasketItemDoesNotExist(Exception):
    pass
    
class BasketDoesNotExist(Exception):
    pass
    
# the homepage view
def index(request):
    
    curr = RequestContext(request)['currency']
    
    teas = Product.objects.filter(
            is_active=True, 
            is_featured=True,     
            category__parent_category__slug=_('teas')
            )[:4]
            
    for t in teas:
        t.price = t.get_lowest_price(currency=curr)
        
    blog_entries = BlogEntry.objects.filter(is_promoted=True, is_draft=False)[:3]
            
    teaware = Product.objects.filter(
        is_active=True,
        is_featured=True,
        category__parent_category__slug=_('teaware'),
    )[:4]
    
    for t in teaware:
        t.price = t.get_lowest_price(currency=curr)
    
    try:
        special = get_object_or_404(Product, id=54)
        special.price = special.get_lowest_price(curr)
    except:
        pass
     
    return _render(request, "shop/home.html", locals())


def page(request, slug):
    
    page = get_object_or_404(Page, slug=slug)

    if page.slug == _('contact-us'):
        form = ContactForm()
    
    if page.slug == _('learn'):
        pages = Page.objects.filter(parent__parent__slug=_('learn')).order_by('?')[:10]
    
    template = "shop/page.html"
    if page.template:
        template = page.template
    teas = _get_products(request, random=True)[:2]
    
    print "we get here"
    
    return _render(request, template, locals())


def page_by_id(request, id):
    this_page = get_object_or_404(Page, pk=id)
    return page(request, this_page.slug) 
   
   
# the product listing page
def category(request, slug):
    curr = _get_currency(request)
    if slug == _('teas') or slug == _('teaware'):
        products = None
        category = get_object_or_404(Category, slug=slug)
        categories = Category.objects.filter(parent_category__slug=slug)
        for c in categories:
            c.products = _get_products(request, c.slug)
                
    else:
        category = get_object_or_404(Category, slug=slug)
        products = _get_products(request, category.slug)
    
    basket = _get_basket(request)
    if basket and products:
        for x in products: 
            basket_item = BasketItem.objects.filter(basket=basket, item=x.get_lowest_price(curr))
            x.price = x.get_lowest_price(curr)
            if basket_item.count() > 0:
                x.basket_quantity = basket_item[0].quantity
            
    return _render(request, "shop/category.html", locals())

def category_by_id(request, id):
    cat = get_object_or_404(Category, pk=id)
    return category(request, cat.slug)


def germany(request):
    _set_currency(request, 'EUR')
    response = _changelang(request, code='de')
    return response


def italy(request):
    _set_currency(request, 'EUR')
    response = _changelang(request, code='it')
    return response


def sale(request):
    category = get_object_or_404(Category, slug=_('sale'))
    ups = UniqueProduct.objects.filter(is_active=True, sale_price__isnull=False, currency=_get_currency(request))
    products = []
    for x in ups:
        p = x.parent_product
        p.price = x
        products.append(p)
        
    return _render(request, "shop/category.html", locals())



# VIEW FOR A SINGLE PRODUCT
def tea_view(request, slug):
    
    try:
        added = request.session['ADDED']
    except:
        added = None
       
    if added:
        try:
	        thing = get_object_or_404(BasketItem, id=request.session['ADDED'])    
	        from shop.templatetags.convert_weights import convert_weights
	        weight = convert_weights(request, thing.item.weight)
	        message = _("1 x %(weight)s%(unit)s added to your basket!") % {'weight': weight, 'unit': RequestContext(request)['weight_unit']}
	        request.session['ADDED'] = None
        except:
	        pass
    
    tea = get_object_or_404(Product, slug=slug)
    reviews = Review.objects.filter(is_published=True, product=tea, lang=get_language())
    
    # IF IT'S A MONTHLY ITEM, LET'S REDIRECT HERE:
    if tea.slug == _('monthly-tea-box'):
        return monthly_tea_box(request)
    
    recommended = _get_products(request, random=True, exclude=tea.id)[:4]
    prices = UniqueProduct.objects.filter(is_active=True, parent_product=tea, 
        currency=_get_currency(request)).order_by('weight')

    return _render(request, "shop/tea_view.html", locals())

def product_by_id(request, id):
    product = get_object_or_404(Product, pk=id)
    return tea_view(request, product.slug)


def monthly_tea_box(request):
        
    product = get_object_or_404(Product, slug=_('monthly-tea-box'))
    products = Product.objects.filter(category__parent_category__slug=_('teas'), 
        is_active=True)
        
    basket_items = BasketItem.objects.filter(basket=_get_basket(request))
    
    try:
        months = int(request.session['MONTHS'])
    except:
        months = settings.TEABOX_DEFAULT_MONTHS
    
    
    if product.is_active:
        excluded = []
        total_quantity = 0    
        for x in products:
            
            x.single_price = x.get_lowest_price(_get_currency(request), exclude_sales=True)
            
            if not x.single_price.stocks():
                excluded.append(x.id)
                continue
                # weird... the above thing doesn't work.
            
            try:
                x.price = _get_monthly_price(x.single_price, months)
            except:
                x.price = None
            
            x.quantity = 0
            for y in basket_items:
                if x.single_price == y.item:
                    x.quantity += y.quantity
                    total_quantity += 1
        
        products.exclude(id__in=excluded, name__icontains=_("taster"))   
    
    return _render(request, 'shop/monthly_tea_box.html', locals())
    
def contact_form_submit(request, xhr=None):
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            from emailer.views import _admin_notify_contact
            _admin_notify_contact(form.cleaned_data)
            return _render(request, 'shop/forms/contact_form_thanks.html', locals())
        else:
            page = get_object_or_404(Page, slug='contact-us')
            return _render(request, 'shop/forms/contact_form.html', locals())            
    
    url = reverse('page', args=['contact-us'])
    return HttpResponseRedirect(url)       
   
# function for adding stuff to your basket
def add_to_basket(request, id):
    uproduct = get_object_or_404(UniqueProduct, pk=id)
    basket = _get_basket(request)
     
    try:
        item = get_object_or_404(BasketItem, basket=basket, item=uproduct, monthly_order=False)
        item.quantity += 1
    except:
        item = BasketItem.objects.create(item=uproduct, quantity=1, basket=basket)
    item.save()

    if request.is_ajax():

        message = render_to_string('shop/snippets/added_to_basket.html', {
                    'item':item.item.parent_product, 
                    'weight': item.item.weight, 
                    'weight_unit': RequestContext(request)['weight_unit'],
                    'url': reverse('basket'),
        })
        
        basket_amount = '%.2f' % float(_get_basket_value(request)['total_price'])
        basket_quantity = '%.2f' % float(_get_basket_value(request)['basket_quantity'])
        data = {'message': message, 'basket_quantity': basket_quantity, 'basket_amount': basket_amount}
        json =  simplejson.dumps(data, cls=DjangoJSONEncoder)
        return HttpResponse(json)
    
    
    url = request.META.get('HTTP_REFERER','/')
    request.session['ADDED'] = item.id
    return HttpResponseRedirect(url)


def add_to_basket_monthly(request, productID, months):
    
    uproduct = get_object_or_404(UniqueProduct, id=productID)
    basket = _get_basket(request)
   
    try:
        item = get_object_or_404(BasketItem, basket=basket, item=uproduct, monthly_order=True, months=months)
        item.quantity += 1
    except:
        item = BasketItem.objects.create(
            item=uproduct, quantity=1, basket=basket, monthly_order=True, months=months)
        
    item.save()
    
    if request.is_ajax():
        basket = _get_basket_value(request)
        basket_quantity = '%.2f' % float(basket['basket_quantity'])
        monthly_price = '%.2f' % float(basket['monthly_price'])
        basket_value = '%.2f' % float(basket['total_price'])
        
        from shop.templatetags.convert_weights import convert_weights
        weight = convert_weights(request, item.item.weight)
        message = _('<div class="message"><div class="text"><h3>%(months)s months of %(item)s added to your Monthly TeaBox! <a href="%(monthly_url)s">Add more</a> or <a href="%(url)s">Checkout now &raquo;</a></h3></div></div>') % {
                    'months': months,
                    'item':item.item.parent_product, 
                    'url': reverse('basket'),
                    'monthly_url': reverse('monthly_tea_box'),
            }
        
        
        data = {
            'basket_quantity': basket_quantity, 
            'monthly_price': monthly_price, 
            'message': message,
            'basket_value': basket_value,}
        json =  simplejson.dumps(data, cls=DjangoJSONEncoder)
        return HttpResponse(json)
    
    url = request.META.get('HTTP_REFERER','/')
    return HttpResponseRedirect(url)
    

# function for removing stuff from your basket
def remove_from_basket(request, id):
    basket_item = get_object_or_404(BasketItem, pk=id)
    basket_item.delete()
    return HttpResponseRedirect('/basket/')

def reduce_quantity_monthly(request, id):
    uproduct = get_object_or_404(UniqueProduct, pk=id)
    basket = _get_basket(request)
    basket_items = BasketItem.objects.filter(basket=basket)
    
    for x in basket_items:
        if x.item == uproduct:
            if x.quantity == 1:
                x.delete()
            else:
                x.quantity -= 1
                x.save()
            break
    
    url = request.META.get('HTTP_REFERER','/')
    return HttpResponseRedirect(url) 
                


def monthly_order_save(request):

    if request.method == 'POST':
        form = MonthlyBoxForm(request.POST)
        if form.is_valid():
            
            # 1. add a monthly box thing to their basket
            total_quantity = int(form.cleaned_data['frequency']) * int(form.cleaned_data['quantity'])            
            uproduct = form.cleaned_data['tea']
            basket = _get_basket(request)
     
            item = BasketItem.objects.create(
                item=uproduct, 
                quantity=total_quantity, 
                basket=basket, 
                monthly_order=True, 
                months=int(form.cleaned_data['frequency']),
                weight=form.cleaned_data['quantity'],
            )           
            item.save()
                        
            return HttpResponseRedirect(reverse('basket'))
        else:
            pass
        
    return HttpResponseRedirect(reverse('tea_boxes'))


def reduce_quantity(request, basket_item):        
    basket_item = get_object_or_404(BasketItem, pk=basket_item)
    if basket_item.quantity > 1:
        basket_item.quantity -= 1
        basket_item.save()
    else:
        pass
    return HttpResponseRedirect(reverse('basket'))


# function for increasing the quantity of an item in your basket
def increase_quantity(request, basket_item):        
    basket_item = get_object_or_404(BasketItem, pk=basket_item)
    basket_item.quantity += 1
    basket_item.save()
    return HttpResponseRedirect('/basket/') # Redirect after POST



@secure_required
def basket(request):
        
    discount = None
    if request.method == 'POST':
        form = UpdateDiscountForm(request.POST)
        if form.is_valid():
            try:
                discount = get_object_or_404(Discount,
                    discount_code=form.cleaned_data['discount_code'], 
                    is_active=True)
            except:
                discount = None
                
            if discount:
               request.session['DISCOUNT_ID'] = discount.id
            else:
                discount_error_message = _("Sorry, that's not a valid discount code!")
    
    
    basket = _get_basket_value(request, discount=discount)
       
    form = UpdateDiscountForm()
    return _render(request, "shop/basket.html", locals())

def remove_discount(request):
    basket = _get_basket_value(request, discount=None)
    return _render(request, "shop/basket.html", locals())

@secure_required
def order_step_one(request, basket=None):
    
    try:
        basket = Basket.objects.get(id=request.session['BASKET_ID'])
    except:
        pass

    try:
        order = get_object_or_404(Order, id=request.session['ORDER_ID'])
        email = order.owner.email
        house_name_number = order.address.house_name_number
        address_line_1 = order.address.address_line_1
        address_line_2 = order.address.address_line_2
        town_city = order.address.town_city
        postcode = order.address.postcode
        province_state = order.address.province_state
        country = order.address.country
        first_name = order.owner.first_name
        last_name = order.owner.last_name
    except:
        order = None
    
    if not basket and not order:
        problem = _("You don't have any items in your basket, so you can't process an order!")
        return _render(request, 'shop/order-problem.html', locals()) 
            

    if request.method == 'POST': 
        post_values = request.POST.copy()
        initial_values = (
            _('First name'), _('Last name'), _('Email address'),
            _('Your address...'), _(' ...address continued (optional)'),
            _('Town or city'), _('State'), _('Post / ZIP code'), _('invalid'),
            )
            
        for k, v in post_values.iteritems():
            if v in initial_values:
                del post_values[k]
                
        form = OrderStepOneForm(post_values)
        if form.is_valid(): 
            
            # FIRST, GET THE USER
            if request.user.is_authenticated():
                user = request.user
            else:
                                
                try:
                    user = User.objects.filter(email=form.cleaned_data['email'])[0]
                
                except IndexError:
                    creation_args = {
                            'username': form.cleaned_data['email'],
                            'email': form.cleaned_data['email'],
                            'password': uuid.uuid1().hex,
                    }
                    user = User.objects.create(**creation_args)
                    user.first_name = form.cleaned_data['first_name']
                    user.last_name = form.cleaned_data['last_name']
                    user.save()
            
            
            try:
                shopper = get_object_or_404(Shopper, user=user)
            except MultipleObjectsReturned:
                shopper = Shopper.objects.filter(user=user)[0]
            
            except:
                creation_args = {
                    'user': user,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'slug': smart_slugify("".join((form.cleaned_data['first_name'], form.cleaned_data['last_name'])), lower_case=True),
                    'language': get_language(),
                }
                shopper = Shopper.objects.create(**creation_args)
            
                    

            # CREATE AN ADDRESS OBJECT        
            address = Address.objects.create(
                owner = shopper,
                house_name_number = form.cleaned_data['house_name_number'],
                address_line_1 = form.cleaned_data['address_line_1'],
                address_line_2 = form.cleaned_data['address_line_2'],
                town_city = form.cleaned_data['town_city'],
                postcode = form.cleaned_data['postcode'],
                country = form.cleaned_data['country'],
            )
            
            try:
                address.province_state = form.cleaned_data['province_state']
                address.save()
            except:
                pass
            
            # CREATE OR FIND THE ORDER
            try:
                order = get_object_or_404(Order, id=request.session['ORDER_ID'])
                if not order.hashkey:
                    order.hashkey = uuid.uuid1().hex
                    order.save()
                
            except:
                creation_args = {
                    'date_confirmed': datetime.now(),
                    'address': address,
                    'owner': shopper,
                    'status': Order.STATUS_CREATED_NOT_PAID,
                    'invoice_id': "TEMP",
                    'hashkey': uuid.uuid1().hex, 
                }
                order = Order.objects.create(**creation_args)
                order.save() # need to save it first, then give it an ID
                if settings.AFFILIATE_SESSION_KEY in request.session:
                    order.invoice_id = "TEA-00%sA" % (order.id)
                    order.affiliate_referrer = request.session[settings.AFFILIATE_SESSION_KEY]
                else:
                    order.invoice_id = "TEA-00%s" % (order.id)
            
            # DO THEY HAVE A VALID DISCOUNT CODE?
            try: 
                discount = get_object_or_404(Discount, pk=request.session['DISCOUNT_ID'])
                order.discount = discount
            except:
                pass
            
            # UPDATE ORDER WITH THE BASKET ITEMS
            basket_items = BasketItem.objects.filter(basket=basket)
            for item in basket_items:
                order.items.add(item)
                if item.monthly_order:
                    order.monthly_order = True
                
            order.save()
            request.session['ORDER_ID'] = order.id  
 
            # FINALLY! WE'RE DONE
            return HttpResponseRedirect(reverse('order_confirm')) 
        
        # IF THE FORM HAS ERRORS:
        else:
                         
             # LOAD EXISTING DATA
             email = request.POST['email']
             house_name_number = request.POST['house_name_number']
             address_line_1 = request.POST['address_line_1']
             address_line_2 = request.POST['address_line_2']
             town_city = request.POST['town_city']
             postcode = request.POST['postcode']
             country = request.POST['country']
             first_name = request.POST['first_name']
             last_name = request.POST['last_name']
             
             try:
                 province_state = request.POST['province_state']
             except:
                 pass
             
             form = OrderStepOneForm(post_values)

        
    else:
        form = OrderStepOneForm()
    return _render(request, 'shop/forms/order_step_one.html', locals())


def order_url_friend(request, hash):
    
    return order_url(request, hash, friend=True)

@secure_required
def order_url(request, hash, friend=None):
    
    order = get_object_or_404(Order, hashkey=hash)    
    basket = _get_basket_value(request, order=order)
    
    return _render(request, 'shop/forms/order_confirm.html', locals())

@secure_required
def order_repeat(request, hash):

    # THE PREVIOUS ORDER ITEM
    old_order = get_object_or_404(Order, hashkey=hash)
    
    new_order = Order.objects.create(
            date_confirmed = datetime.now(),
            address = old_order.address,
            owner = old_order.owner,
            status = Order.STATUS_CREATED_NOT_PAID,
            invoice_id = "TEMP",
            ) 
    new_order.invoice_id = "TEA-00%s" % (new_order.id)       
    new_order.save()
    
    # it looks silly, but we'll also create a basket for them.
    # because IF they want to add something else to the order, 
    # they'll need a basket.   
    basket = Basket.objects.create(
        date_modified = datetime.now(),
        owner = new_order.owner,
    )
    
    # now we'll check for replacements/substitutions
    currency = _get_currency(request)
    
        
    for item in old_order.items.all():
        if item.item.is_active == False:
            # if it's not available, replace it with the closest matching UniqueProduct
            product = UniqueProduct.objects.filter(
                    parent_product=item.item.parent_product, 
                    sale_price__isnull=True, 
                    currency=currency,
                    is_active=True,
                    ).order_by('-price')[0]
            basket_item = BasketItem.objects.create(item=product, quantity=item.quantity, basket=basket)
            new_order.items.add(basket_item)
        else:
            new_order.items.add(item)
    
    for item in new_order.items.all():
        item.basket = basket
        item.save()
        
    request.session['BASKET_ID'] = basket.id
    request.session['ORDER_ID'] = new_order.id
    
        
    # FINALLY, GET THE VALUES ETC.
    basket = _get_basket_value(request, order=new_order)
        
    return _render(request, 'shop/forms/order_repeat.html', locals())

    
# the view for 'logging out' if you're logged in with the wrong account   
def not_you(request):

	# remember the user's basket, otherwise they 'logout' but lose their own basket.
    this_user = request.user
    basket = Basket.objects.get(id=request.session['BASKET_ID'])
    currency = _get_currency(request)

    
    # log the user out
    if request.user.is_authenticated():
        from django.contrib.auth import load_backend, logout
        for backend in settings.AUTHENTICATION_BACKENDS:
            if this_user == load_backend(backend).get_user(this_user.pk):
                this_user.backend = backend
        if hasattr(this_user, 'backend'):
            logout(request)
            # re-add the basket cookie so they don't lose their items
            
            request.session['BASKET_ID'] = basket.id
            request.session['CURRENCY'] = currency
    
    # now they can return to the usual Step 1 of the form    
    return HttpResponseRedirect('/order/step-one/')    
    
    
    
# the view for the order step 3 - confirming your order
@secure_required
def order_confirm(request):
   
    try:
        order = get_object_or_404(Order, id=request.session['ORDER_ID'])
    except:
        problem = _("You don't have any items in your basket, so you can't process an order!")
        return _render(request, 'shop/order-problem.html', locals())
        
    shopper = order.owner
    order_items = order.items.all() 
        
    basket = _get_basket_value(request, order=order)
    amount_in_cents = int(float(basket['total_price']) * 100) # for stupid stripe...
    
    # THIS HANDLES STRIPE
    if request.method == 'POST':

        stripe.api_key = settings.STRIPE_SECRET_KEY     
        token = request.POST['stripeToken']     
        
        try: 
            charge = stripe.Charge.create( 
                amount=amount_in_cents,  
                currency=basket['currency'].code.lower(), 
                card=token, 
                description=order.owner.user.email 
            ) 
                
            # UPDATE THE ORDER DETAILS
            order.status = Order.STATUS_PAID
            order.date_paid = datetime.now()
            order.save()
    
    
            # IF THERE WAS A SINGLE USE DISCOUNT, UPDATE IT
            if order.discount:
                if order.discount.single_use == True:
                    order.discount.is_active = False
                    order.discount.save()
    
            from emailer.views import _payment_success 
            _payment_success(order)
        
            # NOW CREATE A CUSTOMER PACKAGE
            from logistics.views import _create_customer_package
            _create_customer_package(order)
            
            return HttpResponseRedirect(reverse('order_complete', args=[order.hashkey]))
        except stripe.CardError, e: 
            
            # do we need to do something here like show an error message?!
            
            pass



    return _render(request, 'shop/forms/order_confirm.html', locals())
   


# THIS IS USED AS A CHEAT FOR 100% DISCOUNT ORDERS, FOR TESTING OR WHATEVER
def fake_checkout(request, order_id):
    
    order = get_object_or_404(Order, pk=order_id)
    
    # DOUBLE CHECK THE ORDER HAS 100% DISCOUNT
    if not order.discount or order.discount.discount_value < 1:
        return HttpResponseRedirect(reverse('order_confirm'))
    
    # ORGANISE THE ORDER AS IF IT HAD BEEN PAID LIKE NORMAL
    order.status = Order.STATUS_PAID
    order.date_paid = datetime.now()
    order.notes = '100% discount order, not paid via paypal.'
    order.save()    
    
    from emailer.views import _payment_success
    _payment_success(order)
    
    from shop.utils import _empty_basket
    _empty_basket(request)
    

    return HttpResponseRedirect(reverse('order_complete'))    
    
@secure_required
def order_complete(request, hash=None):

    # TRY TO GET THEIR ORDER INFORMATION FROM A COOKIE
    if hash:
        order = get_object_or_404(Order, hashkey=hash)
    else:
        try:
            order = get_object_or_404(Order, id=request.session['ORDER_ID'])
        except:
            pass
    
    # CLEAR THEIR BASKET (EVERYTHING'S BEEN PAID FOR NOW, RIGHT?)
    from shop.utils import _empty_basket  
    _empty_basket(request)
    
    return _render(request, "shop/order_complete.html", locals())

def order_complete_fake(request):
    
    order = Order.objects.filter(date_paid__isnull=False, is_giveaway=False).order_by('?')[0]
    try:
        request.session['ORDER_ID'] = None
    except:
        pass
    
    try:
        request.session[settings.AFFILIATE_SESSION_KEY] = None # remove this session key now
    except:
        pass
    
    return _render(request, "shop/order_complete.html", locals())

# handles the review/testimonial view
def review_tea(request, category, slug):
    tea = get_object_or_404(Product, slug=slug)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            words = form.cleaned_data['text'] 
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            review = Review.objects.create(
                text=words,
                product=tea,
                first_name=first_name,
                last_name=last_name,
                email=email,
            )
                        
            review.save()
            from emailer.views import _admin_notify_new_review
            _admin_notify_new_review(tea, review)
                                 
            return HttpResponseRedirect(reverse('review_tea_thanks', args=[tea.category.slug, tea.slug]))
        
    else:
        form = ReviewForm()
    return _render(request, "shop/forms/review_form.html", locals())

def review_order(request, hash):
    
    order = get_object_or_404(Order, hashkey=hash)
    
    if request.method == 'POST':
        
        form = ReviewOrderForm(request.POST)
        if form.is_valid():
            words = form.cleaned_data['words'] 
            product = get_object_or_404(Product, pk=form.cleaned_data['product'])
            first_name = order.owner.first_name
            last_name = order.owner.last_name
            email = order.owner.email
            review = Review.objects.create(
                text=words,
                product=product,
                first_name=first_name,
                last_name=last_name,
                email=email,
                date_submitted = datetime.now()
            )
                        
            review.save()
            
            if request.is_ajax():
                data = {'words': words,}
                json =  simplejson.dumps(data, cls=DjangoJSONEncoder)
                return HttpResponse(json)
            
            else:
                pass
    
    return _render(request, 'shop/forms/review_order_form.html', locals())



def review_tea_thanks(request, category, slug):
    message = _("Thanks for posting your review! It's really important to us and we will read and respond to any suggetions you've made.")
    return _render(request, 'shop/message.html', locals())
            

# view for the photo wall
def reviews(request):
    reviews = Review.objects.filter(is_published=True).order_by('-date_submitted')
    return _render(request, 'shop/reviews.html', locals())


    
       