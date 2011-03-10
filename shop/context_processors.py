from django.conf import settings
from minriver.shop.models import *
from minriver import settings


def get_basket(request):
    try:
        basket = Basket.objects.get(id=request.session['BASKET_ID'])
        basket_items = BasketItem.objects.filter(basket=basket)
    except:
        basket_items = None
    return {'basket_items': basket_items}
    
    
def get_basket_quantity(request):
    try:
        basket = Basket.objects.get(id=request.session['BASKET_ID'])
        basket_items = BasketItem.objects.filter(basket=basket)
        basket_quantity = 0
        for item in basket_items:
            basket_quantity += item.quantity
    except:
        basket_quantity = "0"
    
    return {'basket_quantity': basket_quantity}
    
def get_shopper(request):

    # find out if the user is logged in
    if request.user.is_authenticated():

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

def paypal_return(request):
    from django.conf import settings
    return {'paypal_return_url': settings.PAYPAL_RETURN_URL}

def paypal_notify(request):
    from django.conf import settings
    return {'paypal_notify_url': settings.PAYPAL_NOTIFY_URL}

def paypal_business(request):
    from django.conf import settings
    return {'paypal_business_name': settings.PAYPAL_BUSINESS_NAME} 

def paypal_receiver_email(request):
    from django.conf import settings
    return {'paypal_receiver_email': settings.PAYPAL_RECEIVER_EMAIL}  

def paypal_submit_url(request):
    from django.conf import settings
    return {'paypal_submit_url': settings.PAYPAL_SUBMIT_URL}  

def ga_is_on(request):
    from django.conf import settings
    return {'ga_is_on': settings.GA_IS_ON}