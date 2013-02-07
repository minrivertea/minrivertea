from django.conf import settings
from shop.models import *
from blog.models import BlogEntry
from shop.utils import _get_country, _get_currency, _set_currency, _get_region
from django.utils import translation



def common(request):
    context = {}
    context['paypal_return_url'] = settings.PAYPAL_RETURN_URL
    context['paypal_notify_url'] = settings.PAYPAL_NOTIFY_URL
    context['paypal_business_name'] = settings.PAYPAL_BUSINESS_NAME
    context['paypal_receiver_email'] = settings.PAYPAL_RECEIVER_EMAIL
    context['paypal_submit_url'] = settings.PAYPAL_SUBMIT_URL
    context['ga_is_on'] = settings.GA_IS_ON
    context['latestblogs'] = BlogEntry.objects.filter(is_draft=False, title__isnull=False).exclude(title__exact="None").order_by('-date_added')[:3]
    context['static_url'] = settings.STATIC_URL
    context['thumb_large'] = settings.THUMB_LARGE
    context['thumb_home_large'] = settings.THUMB_HOME_LARGE
    context['thumb_medium'] = settings.THUMB_MEDIUM
    context['thumb_small'] = settings.THUMB_SMALL
    context['monthly_discount_low'] = settings.TEABOX_LOW_DISCOUNT * 100
    context['monthly_discount_high'] = settings.TEABOX_HIGH_DISCOUNT * 100


        
    # REGIONAL STUFF
    context['region'] = _get_region(request)    
    if context['region'] == 'US':
        context['weight_unit'] = 'oz'
    else:
        context['weight_unit'] = 'g'
    
    # currency stuff
    context['currency'] = _get_currency(request) 
    


    # CHANGE THE BASE TEMPLATE FOR CHINA
    base_template = settings.BASE_TEMPLATE
    if '/admin-stuff/' in request.path:
        base_template = settings.BASE_TEMPLATE_ADMIN
    
    context['base_template'] = base_template



    # BASKET STUFF
    try:
        basket = Basket.objects.get(id=request.session['BASKET_ID'])
    except:
        basket = None
    
    basket_quantity = 0
    basket_amount = 0
    if basket:
        basket_items = BasketItem.objects.filter(basket=basket)
        for item in basket_items:
            if item.monthly_order:
                basket_quantity += 1
            else:
                basket_quantity += item.quantity
            basket_amount += float(item.get_price())
    
    context['basket_quantity'] = basket_quantity
    context['basket_amount'] = basket_amount    
            
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
