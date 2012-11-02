from django.conf import settings
from minriver.shop.models import *
from minriver.blog.models import BlogEntry
from minriver.shop.views import GetCountry, CURRENCY_CHOICES
from django.utils import translation



def common(request):
    from minriver import settings
    context = {}
    context['paypal_return_url'] = settings.PAYPAL_RETURN_URL
    context['paypal_notify_url'] = settings.PAYPAL_NOTIFY_URL
    context['paypal_business_name'] = settings.PAYPAL_BUSINESS_NAME
    context['paypal_receiver_email'] = settings.PAYPAL_RECEIVER_EMAIL
    context['paypal_submit_url'] = settings.PAYPAL_SUBMIT_URL
    context['ga_is_on'] = settings.GA_IS_ON
    context['latestblogs'] = BlogEntry.objects.filter(is_draft=False).order_by('-date_added')[:3]
    
        
    # REGIONAL STUFF
    try:
        region = request.session['region']
    except:
        region = GetCountry(request)['countryCode']
        # http://en.wikipedia.org/wiki/ISO_3166-1_alpha-2
        request.session['region'] = region
    context['region'] = region


    # CHANGE THE BASE TEMPLATE FOR CHINA
    base_template = settings.BASE_TEMPLATE
    if '/admin-stuff/' in request.path:
        base_template = settings.BASE_TEMPLATE_ADMIN
    else:
        if region == 'CN':
            base_template = settings.BASE_TEMPLATE_CHINA
    context['base_template'] = base_template

    
    # CURRENCIES
    currencycode = 'GBP'    
    try:
        if request.session['CURRENCY']:
            currencycode = request.session['CURRENCY']
    except:
        if region == 'CN':
            currencycode = 'RMB'
                
        if region == 'US':
            currencycode = 'USD'
        
        if region == 'DE':
            currencycode = 'EUR'
            
    currency = Currency.objects.get(code=currencycode)
    context['currency'] = currency 


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
            basket_quantity += item.quantity
            basket_amount += item.get_price()
    
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
