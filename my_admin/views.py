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

import datetime
from datetime import timedelta
import uuid
import re

from shop.utils import _render, pdf
from shop.models import *
from shop.forms import *
from emailer.models import Subscriber
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
    
    if request.GET.get('w'):
        weeks = int(request.GET['w'])
    else:
        weeks = 4
        
    start_date = (datetime.now() - timedelta(weeks=weeks))
    end_date = datetime.now()     
       
    
    if request.GET.get('unpaid'):
        unpaid = True
        packages = Order.objects.filter(
            date_paid__isnull=True, 
            date_confirmed__range=(start_date, end_date)
        ).order_by('-date_confirmed')
    else:
        packages = CustomerPackage.objects.filter(
            created__range=(start_date, end_date), 
            **kwargs
        ).order_by('-created')  

    return _render(request, 'my_admin/orders.html', locals())


def mark_order_as_paid(request, order_id):
    
    order = get_object_or_404(Order, pk=order_id)
    
    # UPDATE THE ORDER DETAILS
    order.status = Order.STATUS_PAID
    order.date_paid = datetime.now()
    order.save()


    # IF THERE WAS A SINGLE USE DISCOUNT, UPDATE IT
    if order.discount:
        if order.discount.single_use == True:
            order.discount.is_active = False
            order.discount.save()


    # NOW CREATE A CUSTOMER PACKAGE
    from logistics.views import _create_customer_package
    _create_customer_package(order)

    url = request.META.get('HTTP_REFERER','/')
    return HttpResponseRedirect(url)

#specific shopper view in admin-stuff
@login_required
def admin_shopper(request, id):
    if not request.user.is_superuser:
        return HttpResponseRedirect("/")
    shopper = get_object_or_404(Shopper, pk=id)
    return _render(request, 'my_admin/shopper.html', locals())


@login_required
def packages_sold(request):
    
    import csv
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=MRT_STOCKS.csv'
    
    writer = csv.writer(response)
    
    start_date = (datetime.now() - timedelta(weeks=int(52)) )
    end_date = datetime.now()
    packages = CustomerPackage.objects.filter(posted__range=(start_date, end_date))
    
    for p in packages:
        try:
            currency = p.postage_currency.code
        except:
            currency = 'GBP'
            
        for x in p.get_items():
            if x.unique_product.parent_product.get_root_category().slug == _('teaware'):
                teaware = 'yes'
            else: 
                teaware = ''
            
        writer.writerow([
            p.posted,
            p.get_items().count(),
            teaware,
            p.order.address.get_country_display(),
            currency,
            p.postage_cost,            
        ])
    
    return response
    

@login_required
def stocks(request):
    
    if request.GET.get('date'):
        
        my_date = datetime.strptime(request.GET.get('date'), "%Y-%M-%d")

        # shows all objects created before this date, but excludes ones sold before
        in_stock = WarehouseItem.objects.filter(created__lte=my_date).exclude(sold__lt=my_date)
        
        import csv
            
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=MRT_STOCKS.csv'

        writer = csv.writer(response)
        for x in in_stock:
            writer.writerow([x.unique_product, x.unique_product.price, x.unique_product.currency])
    
        return response
    
       
    stocks = UniqueProduct.objects.filter(is_active=True, currency__code='GBP')
    
    total_stock_value = 0
    start_date = (datetime.now() - timedelta(weeks=52))
    end_date = datetime.now()
    
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
        
        x.sold_this_year = WarehouseItem.objects.filter(
            unique_product=x,
            sold__range=(start_date, end_date),
        )
        
        total_stock_value += x.total_value
    
    stocks = sorted(stocks, key=lambda x: x.sold_this_year.count(), reverse=True)
    
    form = AddStocksForm()
    products = UniqueProduct.objects.filter(currency__code='GBP', is_active=True)
    return _render(request, 'my_admin/stocks.html', locals())


@login_required
def admin_product(request, id):
    product = get_object_or_404(Product, pk=id)
    
    sold_items = WarehouseItem.objects.filter(
        unique_product__parent_product=product,
        sold__isnull=False,
        )
        
    total_weight = 0
    for x in sold_items:
        total_weight += x.unique_product.weight
    
    start_date = (datetime.now() - timedelta(weeks=52))
    end_date = datetime.now()
    sold_this_year = WarehouseItem.objects.filter(
        unique_product__parent_product=product,
        sold__range=(start_date, end_date),
        )
        
    in_stock = WarehouseItem.objects.filter(
        unique_product__parent_product=product,
        sold__isnull=True,
        )
    
    
    
    

    # if there's a date range, filter by date range.            
                
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
    emails = Subscriber.objects.filter(language='de', date_unsubscribed__isnull=True)
    
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
    
    orders = CustomerPackage.objects.filter(
                order__is_giveaway=False, 
                order__date_paid__range=(start_date, end_date)
                )
    
    tvgbp = 0
    tvusd = 0
    tveur = 0
    total_order_value = 0
    total_items = 0
    av_extra_costs = 0
    pp_cost = 0
    postage_cost = 0
    shoppers = {}
    german_orders_total_value = 0
    italian_orders_total_value = 0
    raph = 0
    german_countries = ('DE', 'AT', 'BE')
    italian_countries = ('IT', 'NL')
    
    for o in orders:
        
        shoppers[o.order.owner] = 1
        
        try:
            code = o.get_final_currency().code
        except AttributeError:
            code = 'GBP'
        
        
        if code == 'GBP':
            currency_converter = 1
            try:
                tvgbp += o.get_final_value()
            except:
                pass
                
        if code == 'USD':
            currency_converter = 0.66
            try:
                tvusd += o.get_final_value() 
            except:
                pass
                
        if code == 'EUR':
            currency_converter = 0.808
            tveur += o.get_final_value()
        
        
        # CALCULATE THE PAYPAL COSTS
        try:
            pp_cost += (float(o.order.get_paypal_ipn().mc_fee) * float(currency_converter))
        except:
            pass
        
        
        try:
            total_items += o.get_items().count()
        except:
            pass
        
        # CALCULATE ABSOLUTE TOTAL AMOUNT IN GBP
        try:       
            total_order_value += float(o.get_final_value()) * float(currency_converter)
        except:
            pass
        
        # CALCULATE THE POSTAGE COSTS
        try:
            postage_cost += float(o.postage_cost) * float(currency_converter)
        except:
            pass    
        
        if o.order.address.country in german_countries:
            amount = float(o.order.get_amount()) * float(currency_converter)
            german_orders_total_value += float(amount)
        
        
        if o.order.address.country in italian_countries:
            amount = float(o.order.get_amount()) * float(currency_converter)
            italian_orders_total_value += float(amount)
            
    
    total_extra_costs = float(pp_cost) + float(postage_cost)
    shoppers = len(shoppers)
    
    # AVERAGES
    av_paypal = pp_cost / orders.count()
    av_postage = postage_cost / orders.count()
    av_order_value = float(total_order_value) / float(orders.count())
    av_order_items = float(total_items) / float(orders.count())
    
    return _render(request, 'my_admin/stats.html', locals())    


@login_required
def print_packing_slip(request, id):
    
    
    package = CustomerPackage.objects.get(pk=id) 
    
    #barcode_number = sendin_request.get_barcode()

    #barcode_image(barcode_number)
    #for _each in UserAddress.objects.filter(user=sendin_request.user):
    #    user_address = _each
    #    break

    #return _render(request, 'my_admin/print_packing_slip.html', locals())
    return pdf('my_admin/print_packing_slip.html', locals())