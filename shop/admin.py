from minriver.shop.models import *
from django.contrib import admin

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}

admin.site.register(Product, ProductAdmin)
admin.site.register(Address)
admin.site.register(Shopper)
admin.site.register(UniqueProduct)
admin.site.register(Basket)
admin.site.register(Order)
admin.site.register(Discount)
admin.site.register(Photo)
admin.site.register(Referee)
admin.site.register(WeLike)



