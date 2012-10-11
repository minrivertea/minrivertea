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


import urllib
import urllib2
import xml.etree.ElementTree as etree
from django.utils import simplejson

import datetime
from datetime import timedelta
import uuid
import twitter
import re

from shop.views import render
from shop.models import *
from shop.forms import *
from slugify import smart_slugify
from shop.emails import _admin_notify_new_review, _admin_notify_contact, _get_subscriber_list




# view for my private admin pages
@login_required
def admin_stuff(request):
    if not request.user.is_superuser:
        raise Http404
    
    # get the stats
    unconfirmed_orders = Order.objects.filter(
        is_confirmed_by_user=True, 
        is_paid=False, 
        is_giveaway=False, 
        reminder_email_sent=False).order_by('-date_confirmed')
    
    if request.GET.get('w'):
        start_date = (datetime.now() - timedelta(weeks=int(request.GET['w'])))
    else:
        start_date = (datetime.now() - timedelta(weeks=4)) 
    
    end_date = datetime.now() 
        
    subscribers = _get_subscriber_list()
    subscriber_count = len(subscribers)
        
    # make the nice lists for paid/unpaid orders
    orders = Order.objects.filter(
        is_giveaway=False, 
        date_paid__range=(start_date, end_date)).exclude(
            status=Order.STATUS_CREATED_NOT_PAID
        ).order_by(
        '-date_paid')
    
    giveaways = Order.objects.filter(is_giveaway=True).order_by('-date_paid')

    return render(request, "my_admin/home.html", locals())

#specific shopper view in admin-stuff
@login_required
def admin_shopper(request, id):
    if not request.user.is_superuser:
        return HttpResponseRedirect("/")
    shopper = get_object_or_404(Shopper, pk=id)
    return render(request, 'my_admin/shopper.html', locals())

def stocks(request):
    stocks = UniqueProduct.objects.filter(is_active=True, currency__code='GBP')
    return render(request, 'my_admin/stocks.html', locals())

@login_required
def admin_product(request, id):
    product = get_object_or_404(Product, pk=id)
    sales = Order.objects.filter(is_paid=True)
    obj_list = []
    for x in sales:
        for i in x.items.all():
            if product == i.item.parent_product:
                obj_list.append(x)
    return render(request, 'my_admin/product.html', locals())

# specific order view in admin-stuff
@login_required
def admin_order(request, id):
    if not request.user.is_superuser:
        return HttpResponseRedirect("/")
    order = get_object_or_404(Order, pk=id)
    return render(request, 'my_admin/order.html', locals())

# function for changing order status from admin-stuff
@login_required
def ship_it(request, id):
    if not request.user.is_superuser:
        return HttpResponseRedirect("/")
    
    order = get_object_or_404(Order, pk=id)    
    order.status = Order.STATUS_SHIPPED
    order.date_shipped = datetime.now()
    order.save()
    
    return HttpResponseRedirect('/admin-stuff')

# form for updating the postage cost of an order
@login_required
def postage_cost_update(request, id):
    if not request.user.is_superuser:
        return HttpResponseRedirect("/")
    order = get_object_or_404(Order, pk=id)
    if request.method == "POST":
        form = PostageCostForm(request.POST)
        if form.is_valid():
            order.postage_cost = form.cleaned_data['cost']
            order.save()
            return HttpResponseRedirect('/admin-stuff')
    return HttpResponseRedirect('/admin-stuff')
    
