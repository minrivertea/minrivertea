from django.conf import settings
from django.http import HttpResponseRedirect

import datetime

from logistics.models import CustomerPackage, WarehouseItem
from logistics.forms import UpdateCustomerPackageForm
from shop.models import Currency




def _create_customer_package(order):
    
    package = CustomerPackage.objects.create(
        order=order,
        created=datetime.now(),
    )

    for x in order.items.all():
        package.items.add(x.item)
        quantity = x.quantity
        wh_items = WarehouseItem.objects.filter(unique_product=x.item)[:(quantity-1)]
        for i in wh_items:
            i.sold = datetime.datetime.now()
            i.reason = WarehouseItem.SOLD
            i.save()
        
    package.save()
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
            
            url = request.META.get('HTTP_REFERER')
            return HttpResponseRedirect(url)
    
    
    return