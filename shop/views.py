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


import urllib
import urllib2
import xml.etree.ElementTree as etree
from django.utils import simplejson

from PIL import Image
from cStringIO import StringIO
import os, md5
import datetime
from datetime import timedelta
import uuid
import twitter
import re



from minriver.shop.models import *
from minriver.shop.forms import *
from minriver.slugify import smart_slugify
from minriver.shop.emails import _admin_notify_new_review, _admin_notify_contact, _wishlist_confirmation_email, _get_subscriber_list, _tell_a_friend_email



class BasketItemDoesNotExist(Exception):
    pass
    
class BasketDoesNotExist(Exception):
    pass
    

#render shortcut
def render(request, template, context_dict=None, **kwargs):
    try:
        region = request.session['region']
    except:
        region = GetCountry(request)['countryCode']
        request.session['region'] = region
      
    if region == 'CN':      
        new_template = "china/%s" % template
        new_template_full = os.path.join(settings.PROJECT_PATH, "templates/", new_template)
        if os.path.exists(new_template_full):
            template = new_template

        
    return render_to_response(
        template, context_dict or {}, context_instance=RequestContext(request),
                              **kwargs
    )

def GetCountry(request):
    # this is coming from http://ipinfodb.com JSON api
    # the variables
    apikey = settings.IPINFO_APIKEY 
    ip = request.META.get('REMOTE_ADDR')
    baseurl = "http://api.ipinfodb.com/v3/ip-country/?key=%s&ip=%s&format=json" % (apikey, ip)
    urlobj = urllib2.urlopen(baseurl)
    
    # get the data
    data = urlobj.read()
    urlobj.close()
    datadict = simplejson.loads(data)
    return datadict


def _get_basket(request):
    # this returns a basket if there is one, or creates it if there isn't one.
    try:
        basket = get_object_or_404(Basket, id=request.session['BASKET_ID'])
    except:
        basket = Basket.objects.create(date_modified=datetime.now())
        basket.save()
        request.session['BASKET_ID'] = basket.id
    
    return basket


def changelang(request, code):
    from django.utils.translation import check_for_language, activate, to_locale, get_language
    next = request.REQUEST.get('next', None)
    if not next:
        next = request.META.get('HTTP_REFERER', None)
    if not next:
        next = '/'
    response = HttpResponseRedirect(next)
    lang_code = code
        
    if lang_code and check_for_language(lang_code):
        if hasattr(request, 'session'):
            request.session[settings.LANGUAGE_COOKIE_NAME] = lang_code
        else:
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
    return response



def twitter_post(tweet):   
    if not twitter or not hasattr(settings, 'TWITTER_USER') or \
        not hasattr(settings, 'TWITTER_PASS'):
        return

    try:
        api = twitter.Api(
                consumer_key=settings.CONSUMER_KEY,
                consumer_secret=settings.CONSUMER_SECRET, 
                access_token_key=settings.ACCESS_TOKEN, 
                access_token_secret=settings.ACCESS_SECRET,
                )
         
        update = api.PostUpdate(tweet)
        
    except Exception, e:
        if settings.DEBUG:
            raise(e)

def _get_currency(request, code=None):
    
    if code:
        code = code
        
    if not code:
        try:
            code = request.session['CURRENCY']
        except:
            code = None
    
    if not code:
        try:
            region = request.session['region']
            if region == 'china':
                code = 'RMB'
                request.session['CURRENCY'] = code
            if region == 'usa':
                code = 'USD'
                request.session['CURRENCY'] = code
        except:
            pass
    

    if not code:
        code = 'GBP'
            
    
    currency = get_object_or_404(Currency, code=code)
    return currency


def GetCountry(request):
    # this is coming from http://ipinfodb.com JSON api
    apikey = settings.IPINFO_APIKEY 
    ip = request.META.get('REMOTE_ADDR')
    baseurl = "http://api.ipinfodb.com/v3/ip-country/?key=%s&ip=%s&format=json" % (apikey, ip)
    urlobj = urllib2.urlopen(baseurl)
    
    # get the data
    url = baseurl + "?" + apikey + "?"
    data = urlobj.read()
    urlobj.close()
    datadict = simplejson.loads(data)
    return datadict


def _get_price(request, items):
    
    total_price = 0
    for item in items:
        price = item.quantity * item.item.price
        total_price += price
    
    currency = _get_currency(request)
    
    if total_price > currency.postage_discount_threshold:
        postage_discount = True
    else:
        total_price += currency.postage_cost
    
    return total_price
    

def _change_currency(request):

    try:
        currency = get_object_or_404(Currency, code=request.GET.get('curr'))
        request.session['CURRENCY'] = currency.code
    except:
        currency = get_object_or_404(Currency, code='GBP')
        request.session['CURRENCY'] = currency.code
    
    
    # if they have a basket already, we need to change the unique products around
    try:
        basket = get_object_or_404(Basket, id=request.session['BASKET_ID'])
        for item in BasketItem.objects.filter(basket=basket):
            newup = get_object_or_404(UniqueProduct,
                is_active=True, 
                parent_product=item.item.parent_product,
                currency=currency,
                weight=item.item.weight)
            item.item = newup
            item.save()
    except:
        pass  
    
    url = request.META.get('HTTP_REFERER','/')
    return HttpResponseRedirect(url)
    
    

def _get_products(request, cat=None):
    if cat:
        products = Product.objects.filter(category=cat, is_active=True).order_by('-list_order')
    else:        
        products = Product.objects.filter(is_active=True).order_by('-list_order')
    
    return products   



# the homepage view
def index(request):
    
    try:
        if request.session['region'] == 'CN':
            teas = Product.objects.filter(category__parent_category__slug='teas', is_featured=True)
            cups = Product.objects.filter(category__slug='teaware')[:3]
            reviews = Review.objects.filter(is_published=True).order_by('?')[:3]
            return render(request, 'shop/home.html', locals())
    except:
        pass
         
    seen = {}
    reviews_one = []
    for item in Review.objects.filter(is_published=True).order_by('?'):
        marker = item.product
        if marker in seen: continue
        seen[marker] = 1
        reviews_one.append(item)
    
    reviews = reviews_one[:5]
    curr = _get_currency(request)
    special = get_object_or_404(UniqueProduct, parent_product__slug='buddhas-hand-oolong-tea', currency=curr)
        
    return render(request, "shop/home.html", locals())



def page(request, slug, x=None, y=None, z=None):
    page = get_object_or_404(Page, slug=slug)
    
    if request.path == '/contact-us/':
        form = ContactForm()
    
    if x or y or z:
        return HttpResponseRedirect(page.get_absolute_url())
        
    template = "shop/page.html"
    if page.template:
        template = page.template
    teas = Product.objects.filter(is_active=True).order_by('?')[:2]
    return render(request, template, locals())
   
# the product listing page
def category(request):
    if request.path.startswith('/cn/'):
        slug = request.path.strip('/cn/').strip('/')
    else:
        slug = request.path.strip('/')
    category = get_object_or_404(Category, slug=slug)
    products = _get_products(request, category)

    curr = _get_currency(request)
    special = get_object_or_404(UniqueProduct, parent_product__slug='buddhas-hand-oolong-tea', currency=curr)
    return render(request, "shop/category.html", locals())



def sale(request):
    prices = UniqueProduct.objects.filter(is_active=True, is_sale_price=True)
    return render(request, "shop/sale.html", locals())



# view for a single product
def tea_view(request, slug):
    try:
        added = request.session['ADDED']
    except:
        added = None
       
    if added:
        thing = get_object_or_404(BasketItem, id=request.session['ADDED'])
        message = "1 x %s%s added to your basket!" % (thing.item.weight, thing.item.weight_unit)
        request.session['ADDED'] = None
        
    tea = get_object_or_404(Product, slug=slug)
    try:
        price = UniqueProduct.objects.filter(
            parent_product=tea, 
            is_active=True, 
            is_sale_price=False, 
            currency=_get_currency(request),
            ).order_by('price')[0]
    except:
        price = None
    
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
        review = Review.objects.filter(product=tea)[0]
    except:
        pass

    return render(request, "shop/tea_view.html", locals())
    
def contact_form_submit(request, xhr=None):
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            _admin_notify_contact(form.cleaned_data)
            message = _("Thanks! Your message has been sent and we'll get back to you as soon as we can.")
            return render(request, 'shop/forms/contact_form.html', locals())
        else:
            page = get_object_or_404(Page, slug='contact-us')
            return render(request, 'shop/forms/contact_form.html', locals())            
    
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
        
        message = _('<p><img src="/static/images/tick.png"/><strong>1 x %s</strong> added to your basket!<br/><br/> <a href="/basket/"><strong>Checkout now &raquo;</strong></a></p>') % item.item 
        data = {'quantity': basket_quantity, 'item': message}
        json =  simplejson.dumps(data, cls=DjangoJSONEncoder)
        return HttpResponse(json)
    
    else:
        url = request.META.get('HTTP_REFERER','/')
        request.session['ADDED'] = item.id
        return HttpResponseRedirect(url)


# function for removing stuff from your basket
def remove_from_basket(request, productID):
    product = get_object_or_404(UniqueProduct, id=productID)
    if request.user.is_anonymous:
        #try to find out if they alread have a session cookie open with a basket
        try:
            basket = get_object_or_404(Basket, id=request.session['BASKET_ID'])
        # if not, we'll return an error because nobody can remove an item 
        # from a basket that doesn't exist
        except BasketDoesNotExist:
            pass
    
    item = BasketItem.objects.get(
        basket=basket,
        item=product,
    )
    item.delete()
    
    return HttpResponseRedirect('/basket/') # Redirect after POST
    
# function for reducing the quantity of an item in your basket    
def reduce_quantity(request, productID):
    product = get_object_or_404(UniqueProduct, id=productID)
    
    # GET THE USER'S BASKET
    if request.user.is_anonymous:
        try:
            basket = get_object_or_404(Basket, id=request.session['BASKET_ID'])
        except BasketDoesNotExist:
            pass
    
    basket_item = BasketItem.objects.get(basket=basket, item=product)
    if basket_item.quantity > 1:
        basket_item.quantity -= 1
        basket_item.save()
    else:
        pass
    
    return HttpResponseRedirect('/basket/') # Redirect after POST


# function for increasing the quantity of an item in your basket
def increase_quantity(request, productID):
    product = get_object_or_404(UniqueProduct, id=productID)
    
    # GET THE USER'S BASKET
    if request.user.is_anonymous:
        try:
            basket = get_object_or_404(Basket, id=request.session['BASKET_ID'])
        except BasketDoesNotExist:
            pass

    
    basket_item = BasketItem.objects.get(basket=basket, item=product)
    basket_item.quantity += 1
    basket_item.save()
    
    return HttpResponseRedirect('/basket/') # Redirect after POST


# the view for your basket
def basket(request):
    try:
        basket = get_object_or_404(Basket, id=request.session['BASKET_ID'])
    except:
        basket = None        
                
    basket_items = BasketItem.objects.filter(basket=basket)
    
    # work out the price
    total_price = 0
    for item in basket_items:
        price = item.quantity * item.item.price
        total_price += price
    
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
            return render(request, "shop/basket.html", locals())
    
    form = UpdateDiscountForm()
        
    return render(request, "shop/basket.html", locals())



# the view for order process step 1 - adding your details
def order_step_one(request):
    
    # first off, check that they have a basket
    try:
        basket = Basket.objects.get(id=request.session['BASKET_ID'])
    except:
        problem = _("You don't have any items in your basket, so you can't process an order!")
        return render(request, 'shop/order-problem.html', locals())   

    # next, if they already have an order, try loading the information
    try:
        order = get_object_or_404(Order, id=request.session['ORDER_ID'])
        
        # load their data from cookie
        if not order == None:    
            email = order.owner.email
            house_name_number = order.address.house_name_number
            address_line_1 = order.address.address_line_1
            address_line_2 = order.address.address_line_2
            town_city = order.address.town_city
            postcode = order.address.postcode
            country = order.address.country
            first_name = order.owner.first_name
            last_name = order.owner.last_name
    except:
        pass
    
    # check if they're secretly logged in
    if request.user.is_authenticated():
        shopper = get_object_or_404(Shopper, user=request.user.id)
    else:
        shopper = None

    # if it's a POST request
    if request.method == 'POST': 
        post_values = request.POST.copy()
        initial_values = (
            _('First name'), _('Last name'), _('Email address'),
            _('Your address...'), _(' ...address continued (optional)'),
            _('Town or city'), _('Post/ZIP code'), _('Province'),
            )
            
        for k, v in post_values.iteritems():
            if v in initial_values:
                del post_values[k]
                
        form = OrderStepOneForm(post_values)
                
        if form.is_valid(): 
            
            # first, if there's a shopper, we don't need new User and Shopper objects
            if not shopper:
                # is there already a shopper with this email?
                try:
                    shopper = get_object_or_404(Shopper, email=form.cleaned_data['email'])
                    this_user = shopper.user
                except:
                    try:
                        # just double check if there's a user object
                        this_user = get_object_or_404(User, email=form.cleaned_data['email'])
                    except:
                        # if there's no user with this email, we create a user and new shopper object
                        creation_args = {
                            'username': form.cleaned_data['email'],
                            'email': form.cleaned_data['email'],
                            'password': uuid.uuid1().hex,
                        }
                     
                        this_user = User.objects.create(**creation_args)
                        this_user.first_name = form.cleaned_data['first_name']
                        this_user.last_name = form.cleaned_data['last_name']
                        this_user.save()
                
                    # now we create a new 'shopper' object too
                    full_name = "%s %s" % (form.cleaned_data['first_name'], form.cleaned_data['last_name'])
                    slugger = smart_slugify(full_name, lower_case=True)
                    shopper = Shopper.objects.create(
                        user = this_user,
                        email = form.cleaned_data['email'],
                        first_name = form.cleaned_data['first_name'],
                        last_name = form.cleaned_data['last_name'],
                        subscribed = form.cleaned_data['subscribed'],
                        slug = slugger,     
                    )
                    
                # we'll secretly log the user in now
                from django.contrib.auth import load_backend, login
                for backend in settings.AUTHENTICATION_BACKENDS:
                    if this_user == load_backend(backend).get_user(this_user.pk):
                        this_user.backend = backend
                if hasattr(this_user, 'backend'):
                    login(request, this_user)
                    
                
            
            # everyone gets an address object created based on the form info         
            address = Address.objects.create(
                owner = shopper,
                house_name_number = form.cleaned_data['house_name_number'],
                town_city = form.cleaned_data['town_city'],
                postcode = form.cleaned_data['postcode'],
                country = form.cleaned_data['country'],
            )
            
            try: 
                address.address_line_1 = form.cleaned_data['address_line_1']
            except:
                pass
            try:
                address.address_line_2 = form.cleaned_data['address_line_2']
            except:
                pass
            
            address.save()
            
            # reset their basket object
            request.session['BASKET_ID'] = basket.id
            
            # now need to find an existing order object, or create a new one:
            
            try:
                order = get_object_or_404(Order, id=request.session['ORDER_ID'])
            except:
                order = Order.objects.create(
                    is_confirmed_by_user = True,
                    date_confirmed = datetime.now(),
                    address = address,
                    owner = shopper,
                    status = Order.STATUS_CREATED_NOT_PAID,
                    invoice_id = "TEMP"
                )
                order.save() # need to save it first, then give it an ID
                order.invoice_id = "TEA-00%s" % (order.id)
            
            # check if the person has inputted a valid discount code?
            try: 
                discount = get_object_or_404(Discount, pk=request.session['DISCOUNT_ID'])
                order.discount = discount
            except:
                pass
            
            # add the items to the order (we put this here not above just in case they added more items)
            basket_items = BasketItem.objects.filter(basket=basket)
            for item in basket_items:
                order.items.add(item)
                
            order.save()
            request.session['ORDER_ID'] = order.id  
 
            return HttpResponseRedirect('/order/confirm') 
        
        # if the form has errors...
        else:
                         
             # load their data if they already tried to submit the form and failed.
             email = request.POST['email']
             house_name_number = request.POST['house_name_number']
             address_line_1 = request.POST['address_line_1']
             address_line_2 = request.POST['address_line_2']
             town_city = request.POST['town_city']
             postcode = request.POST['postcode']
             country = request.POST['country']
             first_name = request.POST['first_name']
             last_name = request.POST['last_name']
             
             form = OrderStepOneForm(post_values)

        
    else:
        form = OrderStepOneForm()
    return render(request, 'shop/forms/order_step_one.html', locals())

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

    return render(request, 'shop/forms/order_confirm.html', locals())


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
    
    return render(request, 'shop/forms/order_repeat.html', locals())

    
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
        
    return render(request, 'shop/forms/wishlist_confirm.html', locals())

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
    
    
    
# the view for the order step 2 - confirming your order
def order_confirm(request):
    
    try:
        basket = get_object_or_404(Basket, id=request.session['BASKET_ID'])
    except:
        problem = _("You don't have any items in your basket, so you can't process an order!")
        return render(request, 'shop/order-problem.html', locals())
        
    order = Order.objects.get(id=request.session['ORDER_ID'])
    shopper = order.owner
    order_items = order.items.all() #BasketItem.objects.filter(basket=basket)
    
    # work out the price
    total_price = 0
    for item in order_items:
        price = item.quantity * item.item.price
        total_price += price
    
    currency = _get_currency(request)
    
    if total_price > currency.postage_discount_threshold:
        postage_discount = True
    else:
        total_price += currency.postage_cost
        
    # is there a discount?
    if order.discount:
        value = total_price * order.discount.discount_value
        percent = order.discount.discount_value * 100
        total_price -= value
        
    if request.method == 'POST': 
        form = OrderCheckDetailsForm(request.POST)
        basket = get_object_or_404(Basket, id=request.session['BASKET_ID'])
        basket.delete()
        new_basket = Basket.objects.create(owner=shopper, date_modified=datetime.now())
        request.session['BASKET_ID'] = new_basket.id
        
        return False
        
        
    else:
        form = PayPalPaymentsForm()

    return render(request, 'shop/forms/order_confirm.html', locals())
   
 
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
    # the user should be logged in here, so we'll find their Shopper object
    # or redirect them to home if they're not logged in
    try:
        shopper = get_object_or_404(Shopper, user=request.user)
    except:
        shopper = None
    

    return render(request, "shop/order_complete.html", locals())


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
    return render(request, "shop/forms/review_form.html", locals())


            

# view for the photo wall
def reviews(request):
    reviews = Review.objects.filter(is_published=True).order_by('product')
    return render(request, 'shop/reviews.html', locals())


# view for a user's "I'm a tea lover" page
def tea_lover(request, slug):
    tea_lover = get_object_or_404(Shopper, slug=slug)
    
    return render(request, 'shop/tea_lover.html', locals())
 
 
 
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
            return render(request, "shop/forms/tell_a_friend.html", locals())

        else:
            if form.non_field_errors():
                non_field_errors = form.non_field_errors()
            else:
                errors = form.errors
             
    else:
        form = TellAFriendForm()
    return render(request, 'shop/forms/tell_a_friend.html', locals())


def international(request):
    request.session['region'] = 'global'
    currency = _change_currency(request)
    request.session['CURRENCY'] = 'GBP'
            
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
        postage_discount = True
    else:
        postage_cost = currency.postage_cost * float(exchange_rate) 
        postage_discount = None
    
    old_total = old_price + currency.postage_cost
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
    
   
    return render(request, 'shop/forms/order_confirm.html', locals())
    
    

def make_product_feed(request):
    products = UniqueProduct.objects.filter(currency__code='GBP', is_active=True)
    
    content = render_to_string('product_feed_template.xml', {'products': products}) 
    return HttpResponse(content, mimetype="application/xml") 
       