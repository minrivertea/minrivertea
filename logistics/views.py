from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse


import datetime
import uuid

from logistics.models import CustomerPackage, WarehouseItem
from logistics.forms import UpdateCustomerPackageForm, AddStocksForm
from shop.models import Currency, UniqueProduct, Order




def _create_customer_package(order):
    
    # create a CustomerPackage
    package = CustomerPackage.objects.create(
        order=order,
        created=datetime.datetime.now(),
    )
    
    preorder_package = None
    
    # iterate through the items the customer has ordered
    for x in order.items.all():
        
        # remember they might have ordered 2+ of the same
        loop = x.quantity
        while loop >= 1:
            try:
                
                # if we have a WHItem available, then add it to the main package
                wh_item = WarehouseItem.objects.filter(unique_product=x.item, sold__isnull=True, available__lte=datetime.datetime.now())[0]
                package.items.add(wh_item)
                package.save()
                wh_item.sold = datetime.datetime.now()
                wh_item.reason = WarehouseItem.SOLD
                wh_item.save()
            
            except:
                
                # if there isn't a WHItem available, create a new one...
                wh_item = WarehouseItem.objects.create(
                    unique_product=x.item,
                    hashkey=uuid.uuid1().hex,
                    created=datetime.datetime.now(),
                    batch='TEMP',
                )
                
                # ...and then add it to a preorder package. 
                if preorder_package == None:
                    preorder_package = CustomerPackage.objects.create(
                        order=order,
                        created=datetime.datetime.now(),
                        is_preorder=True,
                    )

                preorder_package.items.add(wh_item)
                preorder_package.save()
            
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
            up = form.cleaned_data['unique_product']
            batch = form.cleaned_data['batch']
            
            
            while quantity > 0:
                new_item = WarehouseItem.objects.create(
                    unique_product = UniqueProduct.objects.get(id=up),
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
    up = UniqueProduct.objects.get(pk=id)
    stock_in_transit = WarehouseItem.objects.filter(unique_product=up, available=None, sold=None)
    for x in stock_in_transit:
        x.available = datetime.datetime.now()
        x.save()
    
    url = request.META.get('HTTP_REFERER')
    return HttpResponseRedirect(url)
    
    