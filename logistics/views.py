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
from shop.utils import _check_offers


def add_months(sourcedate,months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month / 12
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    return datetime.date(year,month,day)


def _create_customer_package(order):
    """
    Given an order that has been paid for, create a customer package 
    and assign the appropriate stocks to that package. If the items 
    are out of stock, then this function should create new stocks and 
    a seperate Customer Package and mark it as a pre-order
    """
                
    next_date = datetime.datetime.now()
    
    
    # RUN THE ITEMS THROUGH THE OFFERS FILTER, JUST TO CHECK
    items = _check_offers(order.items.filter(monthly_order=False))
    
    
    # GO THROUGH EACH SINGLE ITEM, GET/CREATE A WAREHOUSE ITEM, AND ADD IT TO A PACKAGE
    for x in items:
                
        loop = x.quantity
        while loop >= 1:
            
            try:
                # GET A WAREHOUSE ITEM THAT MATCHES THE CURRENCY PARENT_PRODUCT, WEIGHT AND CURRENCY
                wh_item = WarehouseItem.objects.filter(
                    unique_product__parent_product=x.item.parent_product, 
                    unique_product__weight=x.item.weight,
                    unique_product__currency__code='GBP',
                    sold__isnull=True,
                )[0]
                
                wh_item.sold = datetime.datetime.now()
                wh_item.reason = WarehouseItem.SOLD
                preorder = False                
            
            except: 
                # IF THERE'S NONE IN STOCK, CREATE A NEW ITEM AND MARK THE PACKAGE AS A PREORDER              
                up = UniqueProduct.objects.filter( 
                    currency__code='GBP', 
                    parent_product=x.item.parent_product,
                    weight=x.item.weight,
                    is_active=True,   
                )[0]
                
                wh_item = WarehouseItem.objects.create(
                    unique_product=up,
                    hashkey=uuid.uuid1().hex,
                    created=datetime.datetime.now(),
                    batch='TEMP',
                )
                preorder = True
                
            try:
                package = CustomerPackage.objects.get(
                        order=order, 
                        is_preorder=preorder,
                        )
            except:
                package = CustomerPackage.objects.create(
                        order=order,
                        is_preorder=preorder
                        )

            wh_item.package = package               
            
            # UPDATE THE FINAL FIGURES FOR POSTERITY
            wh_item.sale_currency = x.item.currency
            wh_item.list_price = x.item.price
            wh_item.sale_price = x.item.get_price()
            wh_item.save()
            
            loop -= 1


    # APPLY THE DISCOUNT/POSTAGE COSTS TO ONLY 1 PACKAGE
    try:
        package = CustomerPackage.objects.filter(order=order)[0]
        package.discount_amount = order.get_discount()
        
        amount = 0
        for x in order.items.filter(monthly_order=False):
            amount += x.item.price
        
        if amount > order.get_currency().postage_discount_threshold:
            postage_amount = 0
        else:
            postage_amount = order.get_currency().postage_cost
                
        package.postage_paid = postage_amount
        package.save()
    except:
        pass


    # NOTE: WE AREN'T SELLING MONTHLY ITEMS NOW!
    # NOW DEAL WITH THE MONTHLY ITEMS
    for x in order.items.filter(monthly_order=True):
                
        months = x.months  
        while months >= 1:
            
            # THIS WILL CREATE THE FIRST PACKAGE TO BE SENT (ie. THE FIRST MONTH)
            if months == x.months:
                
                
                # CREATE A MONTHLY PACKAGE IF ONE DOESN"T ALREADY EXIST
                if not monthly_package:
                    monthly_package = CustomerPackage.objects.create(
                            order=order,
                            created=datetime.datetime.now(),
                    )
                
                    
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
                        wh_item.package = package
                        wh_item.save()                       
                    
            # FOR ALL OTHER MONTHS
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

    return
    
    
    
    
def update_package(request, id):
    
    if request.method == 'POST':
        form = UpdateCustomerPackageForm(request.POST)
        if form.is_valid():
            
            # THIS UPDATES THE PACKAGE
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

def update_stock_location(request, id):
    up = get_object_or_404(UniqueProduct, pk=id)

    location = request.GET.get('location', None)

    if location == 'uk':
        stock = WarehouseItem.objects.filter(unique_product=up, sold__isnull=True, 
            location=WarehouseItem.IN_TRANSIT)
        for x in stock:        
            x.available = datetime.datetime.now()
            x.location = WarehouseItem.UK
            x.save()
    
    if location == 'transit':
        stock = WarehouseItem.objects.filter(unique_product=up, sold__isnull=True, 
            location=WarehouseItem.CHINA)
        for x in stock:
            x.location = WarehouseItem.IN_TRANSIT
            x.save()
    
    url = request.META.get('HTTP_REFERER')
    return HttpResponseRedirect(url)
    
    