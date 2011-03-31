from minriver.shop.models import *
from django.contrib import admin

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
   

class OrderAdmin(admin.ModelAdmin):
    list_display = ('invoice_id', 'is_paid', 'notes')


admin.site.register(Product, ProductAdmin)
admin.site.register(Address)
admin.site.register(Shopper)
admin.site.register(UniqueProduct)
admin.site.register(Basket)
admin.site.register(Order, OrderAdmin)
admin.site.register(Discount)
admin.site.register(Photo)
admin.site.register(Referee)
admin.site.register(WeLike)



