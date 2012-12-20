from logistics.models import *
from django.contrib import admin


class WarehouseItemAdmin(admin.ModelAdmin):
    list_filter = ('sold', 'unique_product')
    list_display = ('hashkey', 'unique_product', 'sold', 'package')    

class CustomerPackageAdmin(admin.ModelAdmin):
    list_filter = ('posted',)
    list_display = ('order', 'posted', 'postage_cost')
    ordering = ('-order',)    


admin.site.register(WarehouseItem, WarehouseItemAdmin)    
admin.site.register(CustomerPackage, CustomerPackageAdmin)



