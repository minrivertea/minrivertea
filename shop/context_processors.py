from django.conf import settings
from shop.models import *
from blog.models import BlogEntry
from shop.utils import _get_country, _get_currency, _set_currency, _get_region, _get_basket_value
from django.utils import translation
from django.utils.translation import get_language

from django.contrib.sites.models import get_current_site




def common(request):
    context = {}
    context['paypal_return_url'] = settings.PAYPAL_RETURN_URL
    context['paypal_notify_url'] = settings.PAYPAL_NOTIFY_URL
    context['paypal_business_name'] = settings.PAYPAL_BUSINESS_NAME
    context['paypal_receiver_email'] = settings.PAYPAL_RECEIVER_EMAIL
    context['paypal_submit_url'] = settings.PAYPAL_SUBMIT_URL
    context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
    context['stripe_secret_key'] = settings.STRIPE_SECRET_KEY
    
    context['ga_is_on'] = settings.GA_IS_ON
    context['latestblogs'] = BlogEntry.objects.filter(is_draft=False, title__isnull=False).exclude(title__exact="None").order_by('-date_added')[:3]
    context['static_url'] = settings.STATIC_URL
    context['thumb_large'] = settings.THUMB_LARGE
    context['thumb_home_large'] = settings.THUMB_HOME_LARGE
    context['thumb_medium'] = settings.THUMB_MEDIUM
    context['thumb_small'] = settings.THUMB_SMALL
    context['monthly_discount_low'] = settings.TEABOX_LOW_DISCOUNT * 100
    context['monthly_discount_high'] = settings.TEABOX_HIGH_DISCOUNT * 100
    
    
    # STUFF RELATED TO COUNTRY SPECIFIC SITES
    context['site_url'] = "http://www.minrivertea.com"
    context['analytics_id'] = settings.ANALYTICS_ID
    context['mailchimp_list_id'] = settings.MAILCHIMP_LIST_ID  
         
    if get_language() == 'de':
        context['mailchimp_list_id'] = settings.GERMAN_MAILCHIMP_LIST_ID
    elif get_language() == 'it':
        context['mailchimp_list_id'] = settings.ITALIAN_MAILCHIMP_LIST_ID
        
        
    context['site_name'] = settings.SITE_NAME # the loose non-techy name

    # GET THE NAVIGATIONS
    context['main_nav'] = Category.objects.filter(is_navigation_item=True).order_by('list_order')
    context['top_nav'] = Page.objects.filter(is_top_nav=True).order_by('list_order')
        
    # REGIONAL STUFF
    context['region'] = _get_region(request)    
    if context['region'] == 'US':
        context['weight_unit'] = 'oz'
    else:
        context['weight_unit'] = 'g'
    
    
    # currency stuff
    context['currency'] = _get_currency(request) 
    

    # AFFILIATE STUFF
    if settings.AFFILIATE_SESSION_KEY in request.session:
        context['affiliate_session'] = True
    
    if request.GET.get(settings.AFFILIATE_URL_VARIABLE):
        context['landing_page'] = True # TODO we should change this to specify which landing page it shoudl show


    # CHANGE THE BASE TEMPLATE FOR ADMIN
    base_template = settings.BASE_TEMPLATE
    if '/admin-stuff/' in request.path:
        base_template = settings.BASE_TEMPLATE_ADMIN
    
    context['base_template'] = base_template



    # BASKET STUFF
    try:
        basket = Basket.objects.get(id=request.session['BASKET_ID'])
    except:
        basket = None
    
    
    try:
        context['basket_quantity'] = request.session['BASKET_QUANTITY']
        context['basket_amount'] = request.session['BASKET_AMOUNT']
        ontext['monthly_price'] = basket['monthly_price'] 
        context['monthly_items'] = basket['monthly_items']
    except:
        basket = _get_basket_value(request)
        context['basket_quantity'] = basket['basket_quantity']
        context['basket_amount'] = basket['total_price']  
        context['monthly_price'] = basket['monthly_price'] 
        context['monthly_items'] = basket['monthly_items']
        context['monthly_items_count'] = basket['monthly_items'].count()
    
            
    return context
    
    
def get_shopper(request):
    # find out if the user is logged in
    if request.user.is_authenticated():
        if request.user.is_superuser:
            shopper = None
        else:
            # check if there is a corresponding shopper
            try:
                shopper = get_object_or_404(Shopper, user=request.user)
            # if not, log them out because something's clearly wrong
            except:
                user = request.user
                from django.contrib.auth import load_backend, logout
                for backend in settings.AUTHENTICATION_BACKENDS:
                    if user == load_backend(backend).get_user(user.pk):
                        user.backend = backend
                if hasattr(user, 'backend'):
                    logout(request)
                shopper = None
    else:
        shopper = None
    
    return {'shopper': shopper}
