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
import re

from shop.views import render
from shop.models import *
from shop.forms import *
from slugify import smart_slugify
from emailer.views import _admin_notify_new_review, _admin_notify_contact, _get_subscriber_list
from logistics.models import WarehouseItem, CustomerPackage




# view for my private admin pages
@login_required
def index(request):
    packages = CustomerPackage.objects.filter(postage_cost=None).order_by('-created')        
    return render(request, "my_admin/home.html", locals())




@login_required
def orders(request, **kwargs):
    
    start_date = (datetime.now() - timedelta(weeks=4))
    if request.GET.get('w'):
        start_date = (datetime.now() - timedelta(weeks=int(request.GET['w'])))
    
    end_date = datetime.now()     
    packages = CustomerPackage.objects.filter(created__range=(start_date, end_date), **kwargs).order_by('-created')        

    return render(request, 'my_admin/orders.html', locals())

#specific shopper view in admin-stuff
@login_required
def admin_shopper(request, id):
    if not request.user.is_superuser:
        return HttpResponseRedirect("/")
    shopper = get_object_or_404(Shopper, pk=id)
    return render(request, 'my_admin/shopper.html', locals())


@login_required
def stocks(request):
       
    products = Product.objects.filter(is_active=True).order_by('category')
    for x in products:
        
        x.get_ups = UniqueProduct.objects.filter(parent_product=x, currency__code='GBP', is_active=True)
        
        # how many of each UP are available/in-transit?
        
        for u in x.get_ups: # now we have all the unique products for this product...
            u.available = WarehouseItem.objects.filter(sold=None, unique_product=u).exclude(available=None)
            u.transit = WarehouseItem.objects.filter(sold=None, unique_product=u, available=None)
        
    return render(request, 'my_admin/stocks.html', locals())


@login_required
def admin_product(request, id):
    product = get_object_or_404(Product, pk=id)
    sales = Order.objects.filter(is_paid=True)
    order_count = 0
    total_weight = 0
    total_items = 0
    for x in sales:
        for i in x.items.all():
            if product == i.item.parent_product:
                try: total_weight += (i.item.weight * i.quantity)
                except: pass
                total_items += i.quantity
                order_count += 1
    return render(request, 'my_admin/product.html', locals())

@login_required
def admin_order(request, id):
    if not request.user.is_superuser:
        return HttpResponseRedirect("/")
    order = get_object_or_404(Order, pk=id)
    return render(request, 'my_admin/order.html', locals())

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
            order.status = Order.STATUS_SHIPPED
            order.save()
            url = request.META.get('HTTP_REFERER')
            return HttpResponseRedirect(url)
    return HttpResponseRedirect('/admin-stuff')
    
