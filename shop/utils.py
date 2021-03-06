from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from django.template import RequestContext, Context
from paypal.standard.forms import PayPalPaymentsForm
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound, Http404
from django.template.loader import render_to_string, get_template
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import ugettext as _
from django.utils.translation import get_language, activate
from django.core.exceptions import MultipleObjectsReturned
from django.utils.encoding import smart_str, smart_unicode
from django.db.models import Q

import urllib
import urllib2
import xml.etree.ElementTree as etree
from django.utils import simplejson
from itertools import chain
from decimal import Decimal


from PIL import Image
from cStringIO import StringIO
import os
import datetime
from datetime import timedelta
import uuid
import re
import ho.pisa as pisa
import cgi


from shop.models import *
from shop.forms import *
from slugify import smart_slugify
    

#render shortcut
def _render(request, template, context_dict=None, **kwargs):
        
    return render_to_response(
        template, context_dict or {}, context_instance=RequestContext(request),
                              **kwargs
    )
    
    
# A DECORATOR THAT MAKES A VIEW HTTPS
def secure_required(view_func):
    """Decorator makes sure URL is accessed over https."""
    if settings.DEBUG:
        return view_func
    else:
        def _wrapped_view_func(request, *args, **kwargs):
            if not request.is_secure():
                if getattr(settings, 'HTTPS_SUPPORT', True):
                    request_url = request.build_absolute_uri(request.get_full_path())
                    secure_url = request_url.replace('http://', 'https://')
                    return HttpResponseRedirect(secure_url)
            return view_func(request, *args, **kwargs)
        
    return _wrapped_view_func


def _get_country(request):
    # this is coming from http://ipinfodb.com JSON api
    # the variables
    
    try:
        apikey = settings.IPINFO_APIKEY 
        ip = request.META.get('REMOTE_ADDR')
        baseurl = "http://api.ipinfodb.com/v3/ip-country/?key=%s&ip=%s&format=json" % (apikey, ip)    
        urlobj = urllib2.urlopen(baseurl)
        # get the data
        data = urlobj.read()
        urlobj.close()
        datadict = simplejson.loads(data)
    except:
        # if there's a timeout or something, fuckit - just return dummy USA data
        datadict = {
        	"statusCode" : "OK",
        	"statusMessage" : "",
        	"ipAddress" : "74.125.45.100",
        	"countryCode" : "US",
        	"countryName" : "UNITED STATES",
        	"regionName" : "CALIFORNIA",
        	"cityName" : "MOUNTAIN VIEW",
        	"zipCode" : "94043",
        	"latitude" : "37.3956",
        	"longitude" : "-122.076",
        	"timeZone" : "-08:00"
        }

    return datadict


def _get_basket(request):
    # this returns a basket if there is one, or creates it if there isn't one.
    try:
        basket = Basket.objects.get(pk=request.session['BASKET_ID'])
    except:
        basket = Basket.objects.create(date_modified=datetime.now())
        basket.save()
        request.session['BASKET_ID'] = basket.id
    
    return basket


def _empty_basket(request):
    
    try:
        request.session['BASKET_ID'] = None
    except:
        pass
    try:
        request.session['ORDER_ID'] = None
    except:
        pass
        
    try:
        request.session['BASKET_QUANTITY'] = 0
    except:
        pass
    
    try:
        request.session['BASKET_AMOUNT'] = 0
    except:
        pass
    
    try:
        request.session['DISCOUNT_ID'] = None
    except:
        pass
        
    # REMOVE THEIR AFFILIATE KEY SO THAT IT DOESN'T KEEP REGISTERING SALES AGAINST THIS LEAD.
    try:
        request.session[settings.AFFILIATE_SESSION_KEY] = None 
    except:
        pass
    
    return None


def _apply_deals(items, free_shipping=False, deal_discount=False):
    """ 
    Accepts a list of BasketItems, and returns a list of items
    with altered prices if there are offers running.
    """
    
    new_item_list = []
    matched_deals = []

    for d in Deal.objects.filter(is_active=True):
        if d.expiry_date and d.expiry_date <= datetime.now():
            continue
        
        g1 = False
        g2 = False
        g3 = False
        matched_items = []
        required_number = d.num_products()
                
        for i in items:
            
            if i.quantity < 1:
                continue
            
            if i.item.sale_price:              
                if i.item.parent_product.totm:
                    if i.item.parent_product.totm.month == datetime.now().month:
                        pass
                    else:
                        continue
                else:
                    continue
                        
            # does the item match this deal?
            if d in i.item.pg_1.all() and not g1:
                g1 = True
                matched_items.append({'basket':i.basket, 'item':i.item,'quantity': 1, 'deal':d, 'original': i})
                i.quantity -= 1
                i.save()
                
                if required_number == len(matched_items):
                    g1 = False
                    g2 = False
                    g3 = False
                    matched_deals.append({'deal':d, 'items':matched_items})
                    matched_items = []
                
                if i.quantity < 1:
                    continue
                
            # does the item match this deal?
            if d in i.item.pg_2.all() and not g2:
                g2 = True
                matched_items.append({'basket':i.basket, 'item':i.item,'quantity': 1, 'deal':d, 'original': i})
                i.quantity -= 1
                i.save()
                
                if required_number == len(matched_items):
                    g1 = False
                    g2 = False
                    g3 = False
                    matched_deals.append({'deal':d, 'items':matched_items})
                    matched_items = []
                
                if i.quantity < 1:
                    continue
            
            # does the item match this deal?
            if d in i.item.pg_3.all() and not g3:
                g3 = True
                matched_items.append({'basket':i.basket, 'item':i.item,'quantity': 1, 'deal':d, 'original': i})
                i.quantity -= 1
                i.save()
                
                if required_number == len(matched_items):
                    g1 = False
                    g2 = False
                    g3 = False
                    matched_deals.append({'deal':d, 'items':matched_items})
                    matched_items = []
                
                if i.quantity < 1:
                    continue   
     
        
        # end of the deal - 
        # if there's anything left in the matched_items, let's give them back
        for m in matched_items:
            m['original'].quantity += m['quantity']
            m['original'].save()
         
    
    if not matched_deals:
        new_item_list = items
        return new_item_list, locals()
    else:
        for i in items:
            if i.quantity > 0:
                new_item_list.append(i)
            else:
                i.delete()
        
    
    # now let's process the deals if there are any
    for m in matched_deals:   
        
        # CREATE SOME NEW REAL BASKET ITEMS
        new_items = []
        for x in m['items']:
            new_item = BasketItem.objects.create(
                basket=x['basket'],
                item=x['item'],
                quantity=x['quantity'],
                )
            new_items.append(new_item)
            new_item_list.append(new_item)
                        
        # FREE SHIPPING
        if m['deal'].free_shipping:
            free_shipping = True
        
        # FIXED DISCOUNT
        if m['deal'].discount_amount:
            deal_discount = m['deal'].discount_amount
                    
        # LAST ITEM FREE
        if m['deal'].last_one_free:
            
            x = new_items[-1]
            x.deal_text = _('%s FOR %s OFFER! You get this one for free!') % (m['deal'].num_products(), (m['deal'].num_products() -1 ) )
            x.original_price = m['items'][-1]['item'].get_price()
            x.deal_price = 0.00   
            print x
            print x.deal_price
                        
        # PERCENT DISCOUNT FOR ITEMS        
        if m['deal'].discount_percent:
                            
            for x in new_items:
                # most simple
                x.deal_text = _('Merry Christmas! This item has been reduced by %s&#37;') % m['deal'].discount_percent
                x.original_price = x.item.get_price()                
                x.deal_price = x.original_price - ( x.original_price * Decimal(m['deal'].discount_percent/100.0) )
            
    return new_item_list, locals() 
        
    
 
def _get_basket_value(request=None, simple=False, order=None, discount=None, basket_quantity=False, total_price=False):    
    
    
    if request:
        if 'BASKET_QUANTITY' in request.session:
            basket_quantity = request.session['BASKET_QUANTITY']

        if 'BASKET_AMOUNT' in request.session:
            total_price = request.session['BASKET_AMOUNT']
        
        if not basket_quantity or total_price:
            request.session['BASKET_QUANTITY'], basket_quantity = float(0), float(0)
            request.session['BASKET_AMOUNT'], total_price = float(0), float(0)
    
        if simple:
            return locals()
    
        currency = _get_currency(request)    
        
    # GET THE ITEMS IN THIS BASKET AND CHECK IF THERE'S ANY DISCOUNTS ACTIVATED
    if order:
        basket_items = BasketItem.objects.filter(basket=order.basket, quantity__gte=0).order_by(
            'item__parent_product__category', '-item__price'
        )
        discount = order.discount
        currency = basket_items[0].item.currency
        
    else:
        basket = _get_basket(request)
        basket_items = BasketItem.objects.filter(basket=basket, quantity__gte=0).order_by(
            'item__parent_product__category', '-item__price'
        )
        try:
            discount = get_object_or_404(Discount, pk=request.session['DISCOUNT_ID'])
        except:
            pass
    

    # WORK OUT THE DEALS OR DISCOUNTS
    total_price = 0
    basket_quantity = 0
    free_shipping = False
    deal_discount = False
    
    if not discount:
        items = _apply_deals(basket_items)
        free_shipping = items[1]['free_shipping']
        deal_discount = items[1]['deal_discount']
        basket_items = items[0] 
        print basket_items
        
    # WORK OUT THE PRICE AGAIN
    for item in basket_items:
        try:
            if item.deal_price > 0:
                total_price += (item.deal_price * item.quantity)
            
        except:
            total_price += item.get_price()
            
        basket_quantity += item.quantity
    
    
    # APPLY ANY DISCOUNT
    if discount:
        discount_value = total_price * discount.discount_value
        discount_percent = float(discount.discount_value * 100)
        total_price -= discount_value
        
    if deal_discount:
        total_price -= deal_discount
    
    if request:
        # RESET THOSE SESSION VARIABLES TOO
        request.session['BASKET_QUANTITY'] = basket_quantity
        request.session['BASKET_AMOUNT'] = total_price
            
    # APPLY THE POSTAGE COSTS
    postage_discount = False
    
    if total_price == 0:
        postage_discount = True
    
    elif total_price > currency.postage_discount_threshold:
        postage_discount = True
        
    elif free_shipping:
        postage_discount = True  
    
    if not postage_discount:          
        total_price += currency.postage_cost
        
    
    return locals() 


def _changelang(request, code):
    
    from django.utils.translation import check_for_language, activate, get_language
        
    if request.GET.get('next'):
        next = request.GET['next']
    else:
        next = '/'
    
    lang_code = code
    
    response = HttpResponseRedirect(next)
    
    if lang_code and check_for_language(lang_code):
        if hasattr(request, 'session'):
            request.session[settings.LANGUAGE_COOKIE_NAME] = lang_code
        else:
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
        
    activate(lang_code)
    
    return response


def _get_region(request):
    try:
        region = request.session['REGION']
    except:
        # http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
        region = _get_country(request)['countryCode']
        request.session['REGION'] = region
        
    return region


def _get_currency(request, currency_code=None):
    
    if not currency_code:    
        try:
            currency_code = request.session['CURRENCY']
        except:
            currency_code = 'GBP'
            region = _get_region(request)
                
            if region == 'US':
                currency_code = 'USD'
            if region == 'DE':
                currency_code = 'EUR'
        
    return get_object_or_404(Currency, code=currency_code)
    

def _set_currency(request, code=None):

    if code:
        request.session['CURRENCY'] = code
        currency = get_object_or_404(Currency, code=code)
    
    else:
        try:
            # check for get parameter in URL (ie. in the header links)
            currency = get_object_or_404(Currency, code=request.GET.get('curr'))
            request.session['CURRENCY'] = currency.code
        except:
            currency = get_object_or_404(Currency, code='GBP')
            request.session['CURRENCY'] = currency.code
    
    try:
        # if they have a basket already, we need to change the unique products around
        basket = _get_basket(request)
        for item in BasketItem.objects.filter(basket=basket):
                        
            newup = UniqueProduct.objects.filter(
                is_active=True, 
                parent_product=item.item.parent_product,
                currency=currency,
                weight=item.item.weight).order_by('price')[0]
            item.item = newup
            item.save()
    except:
        pass
 
    
    url = request.META.get('HTTP_REFERER','/')
    return HttpResponseRedirect(url)
    
    

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
    

def _get_products(request, cat=None, random=False, exclude=None, featured=False):
    
    if cat:
        products = Product.objects.filter(category__slug=cat, is_active=True).order_by('-list_order')
    else:        
        products = Product.objects.filter(is_active=True, name__isnull=False).order_by('-list_order')
   
    if exclude:
        products = products.exclude(pk=exclude)
        
    if random:
        products = products.order_by('?')
    
    if featured:
        products = products.filter(is_featured=True)
        
    
    currency = _get_currency(request)
    for x in products:
        x.price = x.get_lowest_price(currency)
    
    return products   


def _finder(request, x=None, y=None, z=None, slug=None):
    
    current_lang = get_language()
    products = []
    categories = []
    pages = []            

    #  PRODUCTS - IF IT HAS 2 PARTS TO THE URL IT COULD BE A PRODUCT
    if z and slug and not y:
        
        for l in settings.LANGUAGES:
            try:
                activate(l[0])
                p = Product.objects.get(slug=slug)
                products.append(dict(product=p, lang=l[0]))
            except:
                pass

        if len(products) > 0:
            
            if len(products) == 1:
                activate(products[0]['lang'])
                        
            if len(products) > 1:
                activate(current_lang)
                        
            if hasattr(request, 'session'):
                request.session[settings.LANGUAGE_COOKIE_NAME] = get_language()
            else:
                response.set_cookie(settings.LANGUAGE_COOKIE_NAME, get_language())
            
            from shop.views import tea_view
            return tea_view(request, slug)
        else:
            pass

    # CATEGORIES - DOES THE SLUG MATCH A CATEGORY?
    for l in settings.LANGUAGES:
        try:
            activate(l[0])
            c = Category.objects.get(slug=slug)
            categories.append(dict(cat=c.slug, lang=l[0]))
        except:
            pass
    
    if len(categories) > 0:
        if len(categories) == 1:
            activate(categories[0]['lang'])
        
        else:
            activate(current_lang)
        
        if hasattr(request, 'session'):
            request.session[settings.LANGUAGE_COOKIE_NAME] = get_language()
        else:
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, get_language())
        
        from shop.views import category
        return category(request, slug=slug)
            
        
    else:
        pass
     
    
    # PAGES - LAST ONE, TRY TO FIND A MATCHING PAGE
    for l in settings.LANGUAGES:
        try:
            activate(l[0])  
            p = Page.objects.get(slug=slug)
            pages.append(dict(page=p, lang=l[0]))
        except:
            pass  
    
        
    if len(pages) > 0:
        if len(pages) == 1:
            activate(pages[0]['lang'])
        
        if len(pages) > 1:
            activate(current_lang)
        
        
        if hasattr(request, 'session'):
            request.session[settings.LANGUAGE_COOKIE_NAME] = get_language()
        else:
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, get_language())
        
        from shop.views import page
        return page(request, slug=slug)
    
    # RESET TO ORIGINAL LANGUAGE AND SHOW 404
    activate(current_lang)
    raise Http404
    return
    
    
def _get_monthly_price(unique_product, months):
        
    months = int(months)
        
    if unique_product.parent_product.category.slug == _('teaware'):
        return None
    
    if _('taster') in unique_product.parent_product.slug:
        return None
    
    if _('beginners-pack') in unique_product.parent_product.slug:
        return None
    
    if months == 3:
        discount = 0
        
    if months == 6:
        discount = 0
    
    if months == 12:
        discount = float(unique_product.price) * float(settings.TEABOX_LOW_DISCOUNT)

    price = float(unique_product.price) - float(discount)
    total_price = float(price) * months
    
    return total_price



def _change_monthly_frequency(request, months):
    
    # SET A COOKIE WITH THE NUMBER OF MONTHS
    if months == settings.TEABOX_DEFAULT_MONTHS:
        request.session['MONTHS'] = None
    else:
        request.session['MONTHS'] = months
    
    # UPDATE THEIR BASKET 
    basket = _get_basket(request)
    for item in BasketItem.objects.filter(basket=basket, monthly_order=True):
        item.months = months
        item.save()
    
    # RETURN AN AJAX REPONSE   
    if request.is_ajax():
        
        products = Product.objects.filter(
            category__parent_category__slug=_('teas')).exclude(name__icontains=_("taster"))
        
        total_quantity = 0
        for x in products:
            
            x.single_price = x.get_lowest_price(_get_currency(request), exclude_sales=True)
            
            x.price = _get_monthly_price(x.single_price, months)
            
            x.quantity = 0
            
            for y in BasketItem.objects.filter(basket=basket, monthly_order=True):
                if x.single_price == y.item:
                    x.quantity += y.quantity
            
            total_quantity += x.quantity 
                
        html = render_to_string('shop/snippets/products_monthly.html', {
            'teas': products, 
            'months': months,
            'currency': RequestContext(request)['currency'],
            'request': request,
            'weight_unit': RequestContext(request)['weight_unit'],
            'thumb_small': RequestContext(request)['thumb_small'],
        })
        total_quantity = '%s' % total_quantity
        monthly_price = '%.2f' % float(RequestContext(request)['monthly_price'])
        basket_amount = '%.2f' % float(RequestContext(request)['basket_amount'])
        data = {
            'html': html, 
            'total_quantity': total_quantity, 
            'monthly_amount': monthly_price, 
            'months': months,
            'basket_amount': basket_amount,
        }
        json =  simplejson.dumps(data, cls=DjangoJSONEncoder)
        return HttpResponse(json)
    
    
    # RETURN A NORMAL RESPONSE
    url = request.META.get('HTTP_REFERER','/')
    return HttpResponseRedirect(url)


def weight_converter(weight):
    try:
        weight = round((weight / 28.75), 1)
    except TypeError:
        pass
    return weight
    

@login_required
def _internal_pages_list(request):
    
    pages = Page.objects.all()
    products = Product.objects.all()
    categories = Category.objects.all()
    
    from blog.models import BlogEntry
    blogs = BlogEntry.objects.all()
    
    
    return _render(request, 'my_admin/internal_pages_list.html', locals())

# ALL REQUIRED FOR PDF CREATION

def my_link_callback(uri, relative):
    path = os.path.join(settings.PROJECT_PATH, uri)
    if not os.path.isfile(path):
        print "ARR! not a file", repr(path)
    else:
        return path

def pdf(template_path, context):
    """Renders a pdf using the given template and a context dict"""
    template = get_template(template_path)
    context = Context(context)
    html = template.render(context)

    result = StringIO()
    pdf = pisa.pisaDocument(
            StringIO(html.encode('UTF-8')),
            result,
            link_callback=my_link_callback,
            show_error_as_pdf=True,
            debug=True
            )
    #return HttpResponse(html) # for debugging
    if not pdf.err:
        response = HttpResponse(result.getvalue(), mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=mrt-packing-slip.pdf'
        return response
    return HttpResponse('HAHA %s' % cgi.escape(html))
