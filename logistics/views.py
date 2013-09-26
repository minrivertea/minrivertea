from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404


import datetime
import calendar
import uuid

from logistics.models import CustomerPackage, WarehouseItem
from logistics.forms import UpdateCustomerPackageForm, AddStocksForm
from shop.models import Currency, UniqueProduct, Order


def add_months(sourcedate,months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month / 12
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    return datetime.date(year,month,day)


def _create_customer_package(order):
    """
    Given an order that has been paid for, create
    a customer package and assign the appropriate 
    stocks to that package. If the items are out 
    of stock, then this function should create new 
    stocks and a seperate Customer Package and mark 
    it as a pre-order
    """
    
    package = None
    preorder_package = None
    next_date = datetime.datetime.now()
    
    for x in order.items.all():
        
        # IF AN ITEM IS A MONTHLY ORDER
        if x.monthly_order:
            
            # CREATE PACKAGES FOR EACH OF THE MONTHS
            months = x.months  
            while months >= 1:
                
                # IF ITS THE FIRST MONTH:
                if months == x.months:
                    
                    if not package:
                        monthly_package = CustomerPackage.objects.create(
                            order=order,
                            created=datetime.datetime.now(),
                        )
                        package = monthly_package
                    else:
                        monthly_package = package
                        
                    # TAKE THESE ITEMS OUT OF CURRENT AVAILABLE STOCK
                    quantity = x.quantity
                    while quantity >= 1:
                        try:
                            wh_item = WarehouseItem.objects.filter(
                                unique_product__parent_product=x.item.parent_product, 
                                unique_product__weight=x.item.weight,
                                unique_product__currency__code='GBP',
                                sold__isnull=True,
                            )[0]
                        except:
                            wh_item = WarehouseItem.objects.create(
                                unique_product=x.item,
                                hashkey=uuid.uuid1().hex,
                                created=datetime.datetime.now(),
                                batch='TEMP',
                            )
                            
                            wh_item.sold = datetime.datetime.now()
                            wh_item.reason = WarehouseItem.SOLD
                            wh_item.package = monthly_package
                            wh_item.save()                       
                        
                # IF IT'S NOT THE FIRST MONTH:
                else:
                    monthly_package = CustomerPackage.objects.create(
                            order=order,
                            created=datetime.datetime.now(),
                            shipping_due_date=next_date
                    )
                
                    # ADD ITEMS AS PREORDER ITEMS, NOT FROM CURRENT STOCK
                    quantity = x.quantity
                    while quantity >= 1:
                        wh_item = WarehouseItem.objects.create(
                            unique_product=x.item,
                            hashkey=uuid.uuid1().hex,
                            created=datetime.datetime.now(),
                            batch='TEMP',
                        ) 
                                            
                        wh_item.sold = datetime.datetime.now()
                        wh_item.reason = WarehouseItem.SOLD
                        wh_item.package = monthly_package
                        wh_item.save()
                        
                        quantity -= 1
                
                next_date = add_months(next_date, 1)
                months -= 1
            
            
        else:
            loop = x.quantity
            while loop >= 1:
                try:
                    # get a WarehouseItem that matches the parent_product, weight and currency=GBP
                    wh_item = WarehouseItem.objects.filter(
                        unique_product__parent_product=x.item.parent_product, 
                        unique_product__weight=x.item.weight,
                        unique_product__currency__code='GBP',
                        sold__isnull=True,
                    )[0]
                    
                    if not package:
                        package = CustomerPackage.objects.create(
                            order=order,
                            created=datetime.datetime.now(),
                        )
                    package.save()
                    
                    wh_item.sold = datetime.datetime.now()
                    wh_item.reason = WarehouseItem.SOLD
                    wh_item.package = package
                    wh_item.save()
                
                except: 
                    # otherwise, create a warehouse item (because there's none in stock)               
                    up = get_object_or_404(UniqueProduct, 
                        currency__code='GBP', 
                        parent_product=x.item.parent_product,
                        weight=x.item.weight,    
                    )
                    
                    wh_item = WarehouseItem.objects.create(
                        unique_product=up,
                        hashkey=uuid.uuid1().hex,
                        created=datetime.datetime.now(),
                        batch='TEMP',
                    )
                    
                    if not preorder_package:
                        preorder_package = CustomerPackage.objects.create(
                            order=order,
                            created=datetime.datetime.now(),
                            is_preorder=True,
                        )
    
                    preorder_package.save()
                    wh_item.package = preorder_package
                    wh_item.save()
                
                loop -= 1

    return
    
    
    
    
def update_package(request, id):
    
    if request.method == 'POST':
        form = UpdateCustomerPackageForm(request.POST)
        if form.is_valid():
            
            package = CustomerPackage.objects.get(pk=id)
            package.postage_cost = request.POST['postage_cost']
            package.currency = Currency.objects.get(code=request.POST['currency'])
            package.posted = datetime.datetime.now()
            package.save()
            
            package.order.status = Order.STATUS_SHIPPED
            package.order.save()
            
            if request.is_ajax():
                html = '%s%s' % (package.currency.symbol, package.postage_cost)
                return HttpResponse(html)
            
            url = request.META.get('HTTP_REFERER')
            return HttpResponseRedirect(url)
    
    
    return HttpResponseRedirect(reverse('admin_home'))


def add_stocks(request):
    if request.method == 'POST':
        form = AddStocksForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            produced = form.cleaned_data['produced']
            up = form.cleaned_data['unique_product']
            batch = form.cleaned_data['batch']
            
            
            while quantity > 0:
                new_item = WarehouseItem.objects.create(
                    unique_product = up,
                    hashkey=uuid.uuid1().hex,
                    batch=batch, 
                    created=datetime.datetime.now(),
                    location=WarehouseItem.CHINA,
                )
                
                new_item.save()
                quantity -= 1
            
            url = request.META.get('HTTP_REFERER')
            return HttpResponseRedirect(url)
        
    return HttpResponse()

def mark_stock_as_arrived(request, id):
    up = get_object_or_404(UniqueProduct, pk=id)

    stock_in_transit = WarehouseItem.objects.filter(unique_product=up, sold__isnull=True, location=WarehouseItem.CHINA)
    for x in stock_in_transit:
        x.available = datetime.datetime.now()
        x.location = WarehouseItem.UK
        x.save()
    
    url = request.META.get('HTTP_REFERER')
    return HttpResponseRedirect(url)
    
    