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

# APP
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
    curr = _get_currency(request)
    teas = _get_products(request)[:6]
        
    teaware = _get_products(request, cat=_('teaware'))[:3]
    special = get_object_or_404(Product, slug=_('tai-ping-monkey-king'))
    special.price = special.get_lowest_price(curr)
                
    return _render(request, "shop/home.html", locals())


def page(request, slug):
    page = get_object_or_404(Page, slug=slug)
    nav_tree = page.get_nav_tree()
    if page.slug == _('contact-us'):
        form = ContactForm()
    
    if page.slug == _('learn'):
        pages = Page.objects.filter(
            parent__parent__slug=_('learn')
        ).order_by('?')[:10]
    
    template = "shop/page.html"
    if page.template:
        template = page.template
    teas = _get_products(request, random=True)[:2]
    return _render(request, template, locals())


def page_by_id(request, id):
    this_page = get_object_or_404(Page, pk=id)
    return page(request, this_page.slug) 
   
   
# the product listing page
def category(request, slug):
    curr = _get_currency(request)
    if slug == _('teas'):
        products = None
        category = get_object_or_404(Category, slug=slug)
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

def category_by_id(request, id):
    cat = get_object_or_404(Category, pk=id)
    return category(request, cat.slug)


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
    reviews = Review.objects.filter(is_published=True, product=tea, lang=get_language())[:3]
    
    # IF IT'S A MONTHLY ITEM, LET'S REDIRECT HERE:
    if tea.slug == _('monthly-tea-box'):
        return monthly_tea_box(request)
    
    recommended = _get_products(request, random=True, exclude=tea.id)[:3]
    #price = tea.get_lowest_price(_get_currency(request))
    prices = UniqueProduct.objects.filter(is_active=True, parent_product=tea, currency=_get_currency(request)).order_by('weight')
    
    try:
        months = settings.TEABOX_DEFAULT_MONTHS
        monthly_price_up = prices[0]
        monthly_price = _get_monthly_price(monthly_price_up, months)
    except:
        monthly_price = None

    return _render(request, "shop/tea_view.html", locals())

def product_by_id(request, id):
    product = get_object_or_404(Product, pk=id)
    return tea_view(request, product.slug)


def monthly_tea_box(request):
    
    product = get_object_or_404(Product, slug=_('monthly-tea-box'))
    products = Product.objects.filter(category__parent_category__slug=_('teas'), is_active=True).exclude(name__icontains=_("taster"))
    basket_items = BasketItem.objects.filter(basket=_get_basket(request))
    
    try:
        months = int(request.session['MONTHS'])
    except:
        months = settings.TEABOX_DEFAULT_MONTHS
    
    for x in products:
        x.price = x.get_lowest_price(_get_currency(request), exclude_sales=True)
        try:
            x.monthly_price = _get_monthly_price(x.price, months)
        except:
            x.monthly_price = None
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
        if item.item.weight:
            from shop.templatetags.convert_weights import convert_weights
            weight = convert_weights(request, item.item.weight)
            message = render_to_string('shop/snippets/added_to_basket.html', {
                    'item':item.item.parent_product, 
                    'weight': weight, 
                    'weight_unit': RequestContext(request)['weight_unit'],
                    'url': reverse('basket'),
            })
        else:
            message = _('<div class="message"><div class="text"><h3>1 x %(item)s added to your basket! <a href="%(url)s">Checkout now &raquo;</a></h3></div></div>') % {
                    'item':item.item.parent_product, 
                    'url': reverse('basket'),
            }
        basket_quantity = '%.2f' % float(RequestContext(request)['basket_amount'])
        data = {'message': message, 'basket_quantity': basket_quantity}
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
    
    if request.is_ajax():
        basket_quantity = '%.2f' % float(RequestContext(request)['basket_amount'])
        monthly_amount = '%.2f' % float(RequestContext(request)['monthly_amount'])
        
        from shop.templatetags.convert_weights import convert_weights
        weight = convert_weights(request, item.item.weight)
        message = _('<div class="message"><div class="text"><h3>%(months)s months of %(item)s added to your Monthly TeaBox! <a href="%(monthly_url)s">Add more</a> or <a href="%(url)s">Checkout now &raquo;</a></h3></div></div>') % {
                    'months': months,
                    'item':item.item.parent_product, 
                    'url': reverse('basket'),
                    'monthly_url': reverse('monthly_tea_box'),
            }
        
        

        
        data = {'basket_quantity': basket_quantity, 'monthly_amount': monthly_amount, 'message': message,}
        json =  simplejson.dumps(data, cls=DjangoJSONEncoder)
        return HttpResponse(json)
    
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
    monthly = False
    for item in chain(basket_items, monthly_items):
        price = float(item.get_price())
        total_price += float(price)
        if item.monthly_order:
            item.item.weight = item.item.weight * item.quantity
            if item.months >= 6:
                monthly = True
                
    
    currency = _get_currency(request)
    if total_price > currency.postage_discount_threshold or monthly == True:
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
               value = float(total_price) * float(code.discount_value)
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
                if not order.hashkey:
                    order.hashkey = uuid.uuid1().hex
                    order.save()
                
            except:
                creation_args = {
                    'is_confirmed_by_user': True,
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



def order_url(request, hash):
    
    order = get_object_or_404(Order, hashkey=hash)    
    
    regular_items = order.items.exclude(monthly_order=True)
    monthly_items = order.items.filter(monthly_order=True)
    
    total_price = 0
    monthly = False
    
    for item in chain(regular_items, monthly_items):
        price = float(item.get_price())
        total_price += float(price)
        if item.monthly_order:
            if item.months >= 6:
                monthly = True
                
    
    currency = _get_currency(request)
    if total_price > currency.postage_discount_threshold or monthly == True:
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
    currency = _get_currency(request, currency_code=old_order.items.all()[0].item.currency.code)
    for item in old_order.items.all():
        if item.item.is_active == False:
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
    
    regular_items = order.items.exclude(monthly_order=True)
    monthly_items = order.items.filter(monthly_order=True)
        
    # work out the price
    total_price = 0
    for item in order_items:
        total_price += float(item.get_price())
        
    currency = _get_currency(request)
    
    if total_price > currency.postage_discount_threshold:
        postage_discount = True
    else:
        total_price += currency.postage_cost
        
    # is there a discount?
    if order.discount:
        discount = float(total_price) * float(order.discount.discount_value)
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

        _wishlist_confirmation_email(request, wishlist)
  		
        html = render_to_string('shop/snippets/make_wishlist.html', {
                'order': wishlist,
        }, context_instance=RequestContext(request))
        
        json = simplejson.dumps(html, cls=DjangoJSONEncoder)
        return HttpResponse(json, mimetype='application/json')
    

    return   

# THIS IS USED AS A CHEAT FOR 100% DISCOUNT ORDERS, FOR TESTING OR WHATEVER
def fake_checkout(request, order_id):
    
    order = get_object_or_404(Order, pk=order_id)
    
    # DOUBLE CHECK THE ORDER HAS 100% DISCOUNT
    if not order.discount or order.discount.discount_value < 1:
        return HttpResponseRedirect(reverse('order_confirm'))
    
    # ORGANISE THE ORDER AS IF IT HAD BEEN PAID LIKE NORMAL
    order.status = Order.STATUS_PAID
    order.date_paid = datetime.now()
    order.is_paid = True
    order.notes = '100% discount order, not paid via paypal.'
    order.save()    
    
    from emailer.views import _payment_success_email 
    _payment_success_email(order)
    
    from shop.utils import _empty_basket
    _empty_basket(request)

    return HttpResponseRedirect(reverse('order_complete'))    
    
def order_complete(request):

    # TRY TO GET THEIR ORDER INFORMATION FROM A COOKIE
    try:
        order = get_object_or_404(Order, id=request.session['ORDER_ID'])
        request.session['ORDER_ID'] = None
    except:
        pass
    
    # CLEAR THEIR BASKET (EVERYTHING'S BEEN PAID FOR NOW, RIGHT?)
    from shop.utils import _empty_basket  
    _empty_basket(request)
    
    
    # REMOVE THEIR AFFILIATE KEY SO THAT IT DOESN'T KEEP REGISTERING SALES AGAINST THIS LEAD.
    try:
        request.session[settings.AFFILIATE_SESSION_KEY] = None # remove it now
    except:
        pass

    return _render(request, "shop/order_complete.html", locals())

def order_complete_fake(request):
    
    order = Order.objects.filter(is_paid=True, is_giveaway=False).order_by('?')[0]
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
    reviews = Review.objects.filter(is_published=True).order_by('product')
    return _render(request, 'shop/reviews.html', locals())


 
# view for the tell_a_friend form      
def tell_a_friend(request):
        
    if request.method == 'POST':
        form = TellAFriendForm(request.POST)
        if form.is_valid():
            
            # get cleaned data from form submission
            sender = form.cleaned_data['sender']
            receiver = form.cleaned_data['recipient']
            
            _tell_a_friend_email(sender, receiver)

            message = _("We've sent an email to %s letting them know about minrivertea.com - thanks for your help!") % receiver
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
    
    
       