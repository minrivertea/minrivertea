from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import auth
from django.template import RequestContext
from paypal.standard.forms import PayPalPaymentsForm
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseNotFound, Http404
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.translation import ugettext as _
from django.utils.translation import get_language, activate
from django.core.exceptions import MultipleObjectsReturned

from django.db.models import Q


import urllib
import urllib2
import xml.etree.ElementTree as etree
from django.utils import simplejson

from PIL import Image
from cStringIO import StringIO
import os
import datetime
from datetime import timedelta
import uuid
import re


from shop.models import *
from shop.forms import *
from slugify import smart_slugify
    

#render shortcut
def _render(request, template, context_dict=None, **kwargs):
      
    if _get_region(request) == 'CN':      
        new_template = "china/%s" % template
        new_template_full = os.path.join(settings.PROJECT_PATH, "templates/", new_template)
        if os.path.exists(new_template_full):
            template = new_template

        
    return render_to_response(
        template, context_dict or {}, context_instance=RequestContext(request),
                              **kwargs
    )

def _get_country(request):
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


def _changelang(request, code):
    
    from django.utils.translation import check_for_language, activate, to_locale, get_language
    next = '/'

    response = HttpResponseRedirect(next)
    lang_code = code
        
    if lang_code and check_for_language(lang_code):
        if hasattr(request, 'session'):
            request.session[settings.LANGUAGE_COOKIE_NAME] = lang_code
        else:
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
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
            if region == 'CN':
                currency_code = 'RMB'
        
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
        basket = get_object_or_404(Basket, id=request.session['BASKET_ID'])
        for item in BasketItem.objects.filter(basket=basket):
                        
            newup = UniqueProduct.objects.filter(
                is_active=True, 
                parent_product=item.item.parent_product,
                currency=currency,
                weight=item.item.weight)[0]
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
    

def _get_products(request, cat=None, random=False, exclude=None):
    if cat:
        products = Product.objects.filter(category__slug=cat, is_active=True).order_by('-list_order')
    else:        
        products = Product.objects.filter(is_active=True, name__isnull=False).order_by('-list_order')
   
    if exclude:
        products = products.exclude(pk=exclude)
        
    if random == True:
        products = products.order_by('?')
        
    
    currency = _get_currency(request)
    for x in products:
        x.price = x.get_lowest_price(currency)
    
    return products   


def _finder(request, x=None, y=None, z=None, slug=None):
    
    current_lang = get_language()
    products = []
    categories = []
    pages = []
    
    # IF IT HAS 2 PARTS TO THE URL IT COULD BE A PRODUCT - CHECK THIS FIRST
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



    # CATEGORIES FIRST - DOES THE SLUG MATCH A CATEGORY?
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
    


    return HttpResponseNotFound()

def _get_monthly_price(price, months):
    
    discount_amount = float(price) * float(settings.MONTHLY_ORDER_DISCOUNT)
    price = float(price) - float(discount_amount)
    price = float(price) * months
    
    return price

def  weight_converter(weight):
     weight = round((weight / 28.75), 1)
     return weight

