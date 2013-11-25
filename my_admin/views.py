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

from shop.utils import _render, pdf
from shop.models import *
from shop.forms import *
from slugify import smart_slugify
from logistics.models import WarehouseItem, CustomerPackage
from logistics.forms import AddStocksForm




# view for my private admin pages
@login_required
def index(request):
    packages = CustomerPackage.objects.filter(postage_cost=None, shipping_due_date__isnull=True).order_by('-created')
    
    today = datetime.today()
    next_week = (datetime.today() + timedelta(weeks=5))
    
    monthly_packages = CustomerPackage.objects.filter(shipping_due_date__range=(today, next_week), posted__isnull=True).order_by('-created')
    
    return _render(request, "my_admin/home.html", locals())




@login_required
def orders(request, **kwargs):
    
    start_date = (datetime.now() - timedelta(weeks=4))
    if request.GET.get('w'):
        start_date = (datetime.now() - timedelta(weeks=int(request.GET['w'])))
    
    end_date = datetime.now()     
    packages = CustomerPackage.objects.filter(created__range=(start_date, end_date), **kwargs).order_by('-created')        

    return _render(request, 'my_admin/orders.html', locals())

#specific shopper view in admin-stuff
@login_required
def admin_shopper(request, id):
    if not request.user.is_superuser:
        return HttpResponseRedirect("/")
    shopper = get_object_or_404(Shopper, pk=id)
    return _render(request, 'my_admin/shopper.html', locals())


@login_required
def stocks(request):
       
    stocks = UniqueProduct.objects.filter(is_active=True, currency__code='GBP').order_by('-parent_product__category')
    total_stock_value = 0
    for x in stocks:
        x.uk_stocks = WarehouseItem.objects.filter(
            unique_product=x, 
            sold__isnull=True, 
            location=WarehouseItem.UK
        ).order_by('produced', 'created')
        
        x.china_stocks = WarehouseItem.objects.filter(unique_product=x, sold__isnull=True, location=WarehouseItem.CHINA)
        
        x.in_transit_stocks = WarehouseItem.objects.filter(unique_product=x, sold__isnull=True,
            location=WarehouseItem.IN_TRANSIT)
        
        x.total_value = (x.uk_stocks.count() + x.china_stocks.count() + x.in_transit_stocks.count()) * x.price
        
        total_stock_value += x.total_value
    
    form = AddStocksForm()
    products = UniqueProduct.objects.filter(currency__code='GBP', is_active=True)
    return _render(request, 'my_admin/stocks.html', locals())


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
    return _render(request, 'my_admin/product.html', locals())

@login_required
def admin_order(request, id):
    if not request.user.is_superuser:
        return HttpResponseRedirect("/")
    order = get_object_or_404(Order, pk=id)
    return _render(request, 'my_admin/order.html', locals())

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


@login_required
def export_emails(request):
    emails = Subcriber.objects.filter(language='en', date_unsubscribed__isnull=True)
    import csv
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="mrt_emails.csv"'

    writer = csv.writer(response)
    for x in emails:
        writer.writerow([x.email, x.date_signed_up])

    return response

    
@login_required
def stats(request):
    if not request.user.is_superuser:
        return HttpResponseRedirect("/")
    
    start_date = (datetime.now() - timedelta(weeks=260))
    w = None
    if request.GET.get('w'):
        w = request.GET.get('w')
        start_date = (datetime.now() - timedelta(weeks=int(w)))    
    end_date = datetime.now()
    
    orders = CustomerPackage.objects.filter(order__is_paid=True, order__is_giveaway=False, 
        order__date_paid__range=(start_date, end_date))
    
    tvgbp = 0
    tvusd = 0
    tveur = 0
    av_extra_costs = 0
    pp_cost = 0
    postage_cost = 0
    shoppers = {}
    german_orders_total_value = 0
    raph = 0
    german_countries = ('DE', 'AT', 'BE')
    
    for o in orders:
        
        shoppers[o.order.owner] = 1
        
        try:
            code = o.order.get_currency().code
        except AttributeError:
            code = 'GBP'

        # we need to separate currencies
        if code == 'GBP':
            tvgbp += o.order.get_amount()
            try:
                pp_cost += o.order.get_paypal_ipn().mc_fee
            except:
                pass
        if code == 'USD':
            tvusd += o.order.get_amount()
            try:
                pp_cost += (o.order.get_paypal_ipn().mc_fee * 0.66)
            except:
                pass
        if code == 'EUR':
            tveur += o.order.get_amount()
            try:
                pp_cost += (o.order.get_paypal_ipn().mc_fee * 0.808)
            except:
                pass
        
        p = o.postage_cost
        if o.postage_currency != None:
            if o.postage_currency.code == 'EUR':
                p = float(p) * float(0.808)
            if o.postage_currency.code == 'RMB':
                p = float(p) * float(0.1)
            if o.postage_currency.code == 'USD':
                p = float(p) * float(0.66)
        
            postage_cost += float(p)
        
        if o.order.address.country in german_countries:
            amount = o.order.get_amount()
            
            if code == 'EUR':
                amount = float(amount) * float(0.808)
            
            if code == 'USD':
                amount = float(amount) * float(0.66)
            
            german_orders_total_value += float(amount)
            
    
    raph = float(german_orders_total_value) * float(0.1)
    total_extra_costs = float(pp_cost) + float(postage_cost)
    shoppers = len(shoppers)
    
    av_paypal = pp_cost / orders.count()
    av_postage = postage_cost / orders.count()
    av_order_value = (float(tvgbp) + (float(tvusd)*float(0.66)) + (float(tveur)*float(0.808))) / float(orders.count())
    
    return _render(request, 'my_admin/stats.html', locals())    


@login_required
def print_packing_slip(request, id):
    order = get_object_or_404(Order, pk=id)
    #barcode_number = sendin_request.get_barcode()

    #barcode_image(barcode_number)
    #for _each in UserAddress.objects.filter(user=sendin_request.user):
    #    user_address = _each
    #    break

    #return _render(request, 'my_admin/print_packing_slip.html', locals())
    return pdf('my_admin/print_packing_slip.html', locals())