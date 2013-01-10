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


from shop.models import *
from shop.utils import _render, _get_basket, _get_currency, _get_country, _get_region, _changelang, _set_currency, _get_products, _get_monthly_price, weight_converter
from shop.forms import *
from slugify import smart_slugify
from emailer.views import _admin_notify_new_review, _admin_notify_contact, _wishlist_confirmation_email, _get_subscriber_list, _tell_a_friend_email



class BasketItemDoesNotExist(Exception):
    pass
    
class BasketDoesNotExist(Exception):
    pass
    
    

# the homepage view
def index(request):
    
    try:
        if request.session['REGION'] == 'CN':
            teas = Product.objects.filter(category__parent_category__slug=_('teas'), is_featured=True)
            cups = Product.objects.filter(category__slug=_('teaware'))[:3]
            reviews = Review.objects.filter(is_published=True).order_by('?')[:3]
            return _render(request, 'shop/home.html', locals())
    except:
        pass
         
    
    curr = _get_currency(request)
    teas = _get_products(request)[:5]
    teaware = _get_products(request, cat=_('teaware'))[:3]
    
    #special = get_object_or_404(UniqueProduct, parent_product__slug='buddhas-hand-oolong-tea', currency=curr)
        
    return _render(request, "shop/home.html", locals())



def page(request, slug):
    page = get_object_or_404(Page, slug=slug)
    
    if request.path == '/contact-us/':
        form = ContactForm()
    
    template = "shop/page.html"
    if page.template:
        template = page.template
    teas = _get_products(request, random=True)[:2]
    return _render(request, template, locals())
   
   
   
# the product listing page
def category(request, slug):
    curr = _get_currency(request)
    if slug == _('teas'):
        products = None
        category = None
        special = get_object_or_404(UniqueProduct, parent_product__slug=_('buddhas-hand-oolong-tea'), currency=curr)
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


def germany(request):
    _set_currency(request, 'EUR')
    response = _changelang(request, code='de')
    return response


def sale(request):
    category = get_object_or_404(Category, slug=_('sale'))
    ups = UniqueProduct.objects.filter(is_active=True, is_sale_price=True, currency=_get_currency(request))
    products = []
    for x in ups:
        p = x.parent_product
        p.price = x
        products.append(p)
        
    return _render(request, "shop/category.html", locals())



# view for a single product
def tea_view(request, slug):
    try:
        added = request.session['ADDED']
    except:
        added = None
       
    if added:
        thing = get_object_or_404(BasketItem, id=request.session['ADDED'])
        if _get_region(request) == 'US':
            weight = weight_converter(thing.item.weight)
            weight_unit = 'oz'
        else:
            weight_unit = 'g'
            weight = thing.item.weight
        message = _("1 x %(weight)s%(unit)s added to your basket!") % {'weight': weight, 'unit': weight_unit}
        request.session['ADDED'] = None
    
    
    tea = get_object_or_404(Product, slug=slug)
    
    # if it's a monthly package, let's redirect here:
    if tea.slug == _('monthly-tea-box'):
        return monthly_tea_box(request)
    
    recommended = _get_products(request, random=True, exclude=tea.id)[:3]
    
    price = tea.get_lowest_price(_get_currency(request))
    
    try:
        big_price = UniqueProduct.objects.filter(
            parent_product=tea, 
            is_active=True, 
            is_sale_price=False, 
            currency=_get_currency(request),
            weight=500,
        )[0]
    except:
        big_price = None
    
    try:
        monthly_price = _get_monthly_price(price.price, settings.MONTHLY_ORDER_MINIMUM_MONTHS)
    except:
        monthly_price = None
    
    try:
        review = Review.objects.filter(product=tea)[0]
    except:
        pass

    return _render(request, "shop/tea_view.html", locals())

def monthly_tea_box(request):
    
    product = get_object_or_404(Product, slug=_('monthly-tea-box'))
    products = Product.objects.filter(category__parent_category__slug='teas').exclude(name__icontains="taster")
    basket_items = BasketItem.objects.filter(basket=_get_basket(request))
    
    for x in products:
        x.price = x.get_lowest_price(_get_currency(request))
        x.monthly_price = _get_monthly_price(x.price.price, settings.MONTHLY_ORDER_MINIMUM_MONTHS)
        x.quantity = 0
        for y in basket_items:
            if x.price == y.item:
                x.quantity += y.quantity 
    
    return _render(request, 'shop/monthly_tea_box.html', locals())
    
def contact_form_submit(request, xhr=None):
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            _admin_notify_contact(form.cleaned_data)
            message = _("Thanks! Your message has been sent and we'll get back to you as soon as we can.")
            return _render(request, 'shop/forms/contact_form.html', locals())
        else:
            page = get_object_or_404(Page, slug='contact-us')
            return _render(request, 'shop/forms/contact_form.html', locals())            
    
    url = reverse('page', args=['contact-us'])
    return HttpResponseRedirect(url)       
   
# function for adding stuff to your basket
def add_to_basket(request, productID):
    uproduct = get_object_or_404(UniqueProduct, id=productID)
    basket = _get_basket(request)
     
    try:
        item = get_object_or_404(BasketItem, basket=basket, item=uproduct)
        item.quantity += 1
    except:
        item = BasketItem.objects.create(item=uproduct, quantity=1, basket=basket)
        
    item.save()

    if request.is_ajax():
        basket_quantity = 0
        for x in BasketItem.objects.filter(basket=basket):
            basket_quantity += x.quantity
        
        
        weight = None
        weight_unit = None
        if _get_region(request) == 'US':
            if uproduct.weight:
                weight_unit = 'oz'
                weight = weight_converter(uproduct.weight)
        else:
            if uproduct.weight:
                weight_unit = 'g'
                weight = uproduct.weight
        
        
        if weight:
            item_description = "%s (%s%s)" % (uproduct.parent_product.name, weight, weight_unit)
        else:
            item_description = uproduct.parent_product.name
            
        message = _('<p><span class="tick">&#10003;</span><strong>1 x %(item)s</strong> added to your basket!<br/><br/> <a href="/basket/"><strong>Checkout now &raquo;</strong></a></p>') % {'item':item_description}
        data = {'quantity': basket_quantity, 'item': message}
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
        item = BasketItem.objects.create(item=uproduct, quantity=1, basket=basket, monthly_order=True, months=months)
        
    item.save()
    
    url = request.META.get('HTTP_REFERER','/')
    return HttpResponseRedirect(url)
    

# function for removing stuff from your basket
def remove_from_basket(request, id):
    basket_item = get_object_or_404(BasketItem, pk=id)
    basket_item.delete()
    return HttpResponseRedirect('/basket/')


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
    
    return HttpResponseRedirect('/basket/') # Redirect after POST


# function for increasing the quantity of an item in your basket
def increase_quantity(request, basket_item):        
    basket_item = get_object_or_404(BasketItem, pk=basket_item)
    basket_item.quantity += 1
    basket_item.save()
    return HttpResponseRedirect('/basket/') # Redirect after POST


def basket(request):
           
    basket_items = BasketItem.objects.filter(basket=_get_basket(request)).exclude(monthly_order=True)
    monthly_items = BasketItem.objects.filter(basket=_get_basket(request), monthly_order=True)
    
    total_price = 0
    for item in chain(basket_items, monthly_items):
        price = item.get_price()
        total_price += price
        if item.monthly_order:
            item.item.weight = item.item.weight * item.quantity
    
    currency = _get_currency(request)
    
    if total_price > currency.postage_discount_threshold:
        postage_discount = True
    else:
        total_price += currency.postage_cost
        
    
    if request.method == 'POST':
        form = UpdateDiscountForm(request.POST)
        if form.is_valid():
            try:
                code = Discount.objects.get(discount_code=form.cleaned_data['discount_code'], is_active=True)
            except:
                code = None
                
            if code:
               value = total_price * code.discount_value
               percent = code.discount_value * 100
               total_price -= value
               request.session['DISCOUNT_ID'] = code.id
            else:
                discount_message = _("Sorry, that's not a valid discount code!")
            return _render(request, "shop/basket.html", locals())
    
    form = UpdateDiscountForm()
        
    return _render(request, "shop/basket.html", locals())



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
                    user = User.objects.get(email=form.cleaned_data['email'])
                    
                except:
                    creation_args = {
                            'username': form.cleaned_data['email'],
                            'email': form.cleaned_data['email'],
                            'password': uuid.uuid1().hex,
                    }
                    user = User.objects.create(**creation_args)
                    user.first_name = form.cleaned_data['first_name']
                    user.last_name = form.cleaned_data['last_name']
                    user.save()
                
                # SECRETLY LOG THE USER IN
                from django.contrib.auth import load_backend, login
                for backend in settings.AUTHENTICATION_BACKENDS:
                    if user == load_backend(backend).get_user(user.pk):
                        user.backend = backend
                if hasattr(user, 'backend'):
                    login(request, user)
            
            
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
            except:
                creation_args = {
                    'is_confirmed_by_user': True,
                    'date_confirmed': datetime.now(),
                    'address': address,
                    'owner': shopper,
                    'status': Order.STATUS_CREATED_NOT_PAID,
                    'invoice_id': "TEMP"   
                }
                order = Order.objects.create(**creation_args)
                order.save() # need to save it first, then give it an ID
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
            return HttpResponseRedirect('/order/confirm') 
        
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



def order_url(request, hash):
    order = get_object_or_404(Order, hashkey=hash)
    shopper = order.owner
    basket_items = order.items.all()
    order_items = basket_items
    
    total_price = 0
    for item in basket_items:
        price = item.quantity * item.item.price
        total_price += price
    
    currency = _get_currency(request)
    if total_price > currency.postage_discount_threshold:
        postage_discount = True
    else:
        total_price += currency.postage_cost
    
    if order.discount:
        value = total_price * order.discount.discount_value
        percent = order.discount.discount_value * 100
        total_price -= value

    return _render(request, 'shop/forms/order_confirm.html', locals())


def order_repeat(request, hash):
    # reuse an old unpaid order object, or create a new one
    old_order = get_object_or_404(Order, hashkey=hash)
    
    try:
        order = Order.objects.filter(owner=old_order.owner, is_paid=False)[0]
        # we're reusing an old object, so lets clear it...
        for i in order.items.all():
            order.items.remove(i)
    except:
        order = Order.objects.create(
            is_confirmed_by_user = True,
            date_confirmed = datetime.now(),
            address = old_order.address,
            owner = old_order.owner,
            status = Order.STATUS_CREATED_NOT_PAID,
            invoice_id = "TEMP",
        ) 
        order.invoice_id = "TEA-00%s" % (order.id)       

    order.save()
    
    # it looks silly, but we'll also create a basket for them.
    # because IF they want to add something else to the order, they'll need a basket.   
    basket = Basket.objects.create(
        date_modified = datetime.now(),
        owner = order.owner,
    )
    
    # now we'll check for replacements/substitutions
    currency = _get_currency(request, code=old_order.items.all()[0].item.currency.code)
    for item in old_order.items.all():
        if item.item.is_active == False or item.item.parent_product.coming_soon == True:
            # if it's not available, replace it with the closest matching UniqueProduct
            product = UniqueProduct.objects.filter(
                    parent_product=item.item.parent_product, 
                    is_sale_price=False, 
                    currency=currency,
                    is_active=True,
                    ).order_by('-price')[0]
            basket_item = BasketItem.objects.create(item=product, quantity=item.quantity, basket=basket)
            order.items.add(basket_item)
        else:
            order.items.add(item)
    
    for item in order.items.all():
        item.basket = basket
        item.save()
        
    request.session['BASKET_ID'] = basket.id
    request.session['ORDER_ID'] = order.id
    
    total_price = 0
    for item in order.items.all():
        price = item.quantity * item.item.price
        total_price += price
    
    
    if total_price > currency.postage_discount_threshold:
        postage_discount = True
    else:
        total_price += currency.postage_cost
    
    return _render(request, 'shop/forms/order_repeat.html', locals())

    
def wishlist_url(request, hash):
    wishlist = get_object_or_404(Wishlist, hashkey=hash)
    shopper = wishlist.owner
    basket_items = wishlist.wishlist_items.all()
    order_items = basket_items

    total_price = 0
    for item in order_items:
        price = item.quantity * item.item.price
        total_price += price
            
    if total_price > 50:
        postage_discount = True
    else: 
        total_price += 3
    
    select_items_form = SelectWishlistItemsForm()
        
    return _render(request, 'shop/forms/wishlist_confirm.html', locals())

def wishlist_select_items(request):
 
    if request.method == 'POST':
        form = SelectWishlistItemsForm(request.POST)
        if form.is_valid():
            wishlist = get_object_or_404(Wishlist, hashkey=request.POST['hashkey'])
            
            # create an order object and save it:
            order = Order.objects.create(
                owner=wishlist.owner,
                address=wishlist.address,
                date_confirmed=datetime.now(),
                is_confirmed_by_user=True,
                status = Order.STATUS_CREATED_NOT_PAID,
            )
            order.invoice_id = "WL-00%s" % (order.id)
            for item in request.POST.getlist(u'items'):
                order.items.add(BasketItem.objects.get(id=item))
            
            order.save()
            
            # work out the price to display on the page
            total_price = 0
            for item in order.items.all():
                price = item.quantity * item.item.price
                total_price += price
            
            if total_price > 50:
                postage_discount = True
            else: 
                total_price += 3
                postage_discount = False
            
            # create the HTML to send back via AJAX    
            html = render_to_string('shop/snippets/wishlist_order_form.html', {
            	    'order': order,
            	    'postage_discount': postage_discount,
            	    'total_price': total_price,
            	    })
            
            # return the AJAX	    
            return HttpResponse(html, mimetype="text/html")
    
    return HttpResponse()

def wishlist_submit_email(request):
    if request.method == 'POST':
        form = WishlistSubmitEmailForm(request.POST)
        if form.is_valid():
            order = get_object_or_404(Order, id=request.POST['order'])
            # create an order here:
            order.wishlist_payee = request.POST['email']
            order.save()
            total_price = 0
            for item in order.items.all():
                price = item.quantity * item.item.price
                total_price += price
            
            currency = _get_currency(request)
            if total_price > currency.postage_discount_threshold:
                postage_discount = True
            else: 
                total_price += currency.postage_cost
                postage_discount = False
                
            html = render_to_string('shop/snippets/wishlist_complete_form.html', {
            	    'order': order, 
            	    'postage_discount': postage_discount,
            	    'total_price': total_price,
            	    'paypal_submit_url': settings.PAYPAL_SUBMIT_URL,
            	    'paypal_return_url': settings.PAYPAL_RETURN_URL,
            	    'paypal_notify_url': settings.PAYPAL_NOTIFY_URL,
            	    'paypal_receiver_email': settings.PAYPAL_RECEIVER_EMAIL,
            	    })
            return HttpResponse(html, mimetype="text/html")
    
    return HttpResponse()

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
def order_confirm(request):
    
    try:
        basket = get_object_or_404(Basket, id=request.session['BASKET_ID'])
    except KeyError:
        problem = _("You don't have any items in your basket, so you can't process an order!")
        return _render(request, 'shop/order-problem.html', locals())
        
    try:
        order = Order.objects.get(id=request.session['ORDER_ID'])
    except KeyError:
        problem = _("You don't have any items in your basket, so you can't process an order!")
        return _render(request, 'shop/order-problem.html', locals())
        
        
    shopper = order.owner
    order_items = order.items.all() 
    
    # work out the price
    total_price = 0
    for item in order_items:
        total_price += item.get_price()
        
    currency = _get_currency(request)
    
    if total_price > currency.postage_discount_threshold:
        postage_discount = True
    else:
        total_price += currency.postage_cost
        
    # is there a discount?
    if order.discount:
        discount = total_price * order.discount.discount_value
        percent = order.discount.discount_value * 100
        total_price -= discount
        
    if request.method == 'POST': 
        form = OrderCheckDetailsForm(request.POST)
        basket = get_object_or_404(Basket, id=request.session['BASKET_ID'])
        basket.delete()
        new_basket = Basket.objects.create(owner=shopper, date_modified=datetime.now())
        request.session['BASKET_ID'] = new_basket.id
        
        return False
        
        
    else:
        form = PayPalPaymentsForm()

    return _render(request, 'shop/forms/order_confirm.html', locals())
   
 
def order_makewishlist(request):
    
    if request.GET.get('xhr'):
        order = get_object_or_404(Order, id=request.GET.get('order'))
        
        # check if this person already has a wishlist before creating a new one...
        if Wishlist.objects.filter(owner=order.owner):
            objects = Wishlist.objects.filter(owner=order.owner)
            wishlist = objects[0]
            
        else:
            wishlist = Wishlist.objects.create(
                owner = order.owner,
                hashkey = uuid.uuid1().hex,
                address = order.address,
            )
         
        for item in order.items.all():
            wishlist.wishlist_items.add(item)
        
        
        wishlist.save()

        _wishlist_confirmation_email(wishlist)
  		
        html = render_to_string('shop/snippets/make_wishlist.html', {
                'order': wishlist,
        }, context_instance=RequestContext(request))
        
        json = simplejson.dumps(html, cls=DjangoJSONEncoder)
        return HttpResponse(json, mimetype='application/json')
    

    return   
    
    
def order_complete(request):

    try:
        shopper = get_object_or_404(Shopper, user=request.user)
    except:
        shopper = None

    return _render(request, "shop/order_complete.html", locals())


# the user can choose to not have their stuff tweeted
def turn_off_twitter(request, id):
    try:
        shopper = get_object_or_404(Shopper, pk=id)
    except:
        pass
    
    shopper.twitter_username = None
    shopper.save()
    return HttpResponseRedirect('/order/complete/')

# handles the review/testimonial view
def review_tea(request, slug):
    tea = get_object_or_404(Product, slug=slug)
    other_reviews = Review.objects.filter(product=tea, is_published=True)
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
            
            _admin_notify_new_review(tea, review)
                        
            return HttpResponseRedirect('/review/thanks')
        
    else:
        form = ReviewForm()
    return _render(request, "shop/forms/review_form.html", locals())


            

# view for the photo wall
def reviews(request):
    reviews = Review.objects.filter(is_published=True).order_by('product')
    return _render(request, 'shop/reviews.html', locals())


# view for a user's "I'm a tea lover" page
def tea_lover(request, slug):
    tea_lover = get_object_or_404(Shopper, slug=slug)
    
    return _render(request, 'shop/tea_lover.html', locals())
 
 
 
# view for the tell_a_friend form      
def tell_a_friend(request):
        
    if request.method == 'POST':
        form = TellAFriendForm(request.POST)
        if form.is_valid():
            
            # get cleaned data from form submission
            sender = form.cleaned_data['sender']
            receiver = form.cleaned_data['recipient']
            
            _tell_a_friend_email(sender, receiver)

            # create the referrer/referee objects
            try:
                referrer = get_object_or_404(Shopper, email=sender)
                referrer.number_referred += 1
                referrer.save()
            except:
                pass
            
            referee = Referee.objects.create(
                    email=receiver,
                    referred_by=sender,
                    date=datetime.now()
                    )
            referee.save()

            message = _("We've sent an email to %s letting them know about minrivertea.com - thanks for your help!") % referee.email
            # then send them back to the tell a friend page
            return _render(request, "shop/forms/tell_a_friend.html", locals())

        else:
            if form.non_field_errors():
                non_field_errors = form.non_field_errors()
            else:
                errors = form.errors
             
    else:
        form = TellAFriendForm()
    return _render(request, 'shop/forms/tell_a_friend.html', locals())


def international(request):
    request.session['REGION'] = 'global'
    currency = _set_currency(request)
            
    url = request.META.get('HTTP_REFERER','/')
    return HttpResponseRedirect(url)
    
        
def china_convert_prices(request, id):
    order = get_object_or_404(Order, pk=id)
    
    # HACK!! we're going to fake the values just so we can let
    # the customer pay in USD not RMB
    
    exchange_rate = 0.1571 # this is the RMB:USD exchange rate
    
    old_price = 0
    new_price = 0
        
    items = []
    for x in order.items.all():        
        items.append(dict(
            price = float(x.item.price)*float(exchange_rate),
            parent_product = x.item.parent_product.name,
            weight = '%s%s' % (x.item.weight, x.item.weight_unit),
            quantity = x.quantity,
        ))
        old_price += x.item.price
        new_price = float(x.item.price)*float(exchange_rate)
    
    
    
    currency = _get_currency(request)
    if old_price > currency.postage_discount_threshold:
        postage_cost = 0
        postage_discount = True
    else:
        postage_cost = currency.postage_cost * float(exchange_rate) 
        postage_discount = None
    
    old_total = old_price + postage_cost
    new_total = new_price + postage_cost 
          
    paypal_form = render_to_string('shop/snippets/paypal_form_china.html', {
            'order': order,
            'order_items': items,
            'new_price': new_price,
            'old_price': old_price,
            'old_total': old_total,
            'new_total': new_total,
            'exchange_rate': exchange_rate,
            'postage_discount': postage_discount,
            'postage_cost': postage_cost,
            'currency': _get_currency(request, 'USD'),
            'paypal_return_url': settings.PAYPAL_RETURN_URL,
            'paypal_receiver_email': settings.PAYPAL_RECEIVER_EMAIL,
            'paypal_notify_url': settings.PAYPAL_NOTIFY_URL, 
            'paypal_submit_url': settings.PAYPAL_SUBMIT_URL,      
        
        })
    
    if request.is_ajax():
        return HttpResponse(paypal_form)
    
   
    return _render(request, 'shop/forms/order_confirm.html', locals())
    
    

def make_product_feed(request):
    products = UniqueProduct.objects.filter(currency__code='GBP', is_active=True)
    
    content = render_to_string('product_feed_template.xml', {'products': products}) 
    return HttpResponse(content, mimetype="application/xml") 
       