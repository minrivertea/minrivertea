from django.conf import settings
import datetime

from logistics.models import CustomerPackage, WarehouseItem


def _create_customer_package(order):
    
    # CREATE A CUSTOMER PACKAGE
    package = CustomerPackage.objects.create(
        order=order,
        created=datetime.now(),
    )

    # REMOVE WAREHOUSEITEMS FROM AVAILABLE STOCK BY MARKING THEM AS SOLD
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
    
    
def _ship_customer_package(id):
    return