from minriver.shop.models import *
from django.contrib import admin

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        ('Name', {
            'fields': ('name', 'long_name', 'slug', 'meta_title')
        }),
        ('Descriptions', {
            'fields': ('description', 'meta_description', 'super_short_description', 'body_text', 'long_description', 'extra_info')
        }),
        ('Images', {
            'fields': ('image', 'image_2', 'image_2_caption', 'image_3', 'image_3_caption',
                'image_4', 'image_4_caption', 'image_5', 'image_5_caption')
        }),
        ('Others', {
            'fields': ('category', 'is_featured', 'is_active', 'tag_text', 'tag_color',
                'coming_soon', 'list_order', 'recommended')
        }),
    )

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
   
class OrderAdmin(admin.ModelAdmin):
    list_display = ('invoice_id', 'is_paid', 'owner', 'notes')

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'email', 'is_published')
    
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'parent')


class UniqueProductAdmin(admin.ModelAdmin):
    list_display = ('parent_product', 'available_stock', 'weight', 'price', 'is_sale_price', 'is_active', 'currency')
    list_filter = ('is_active', 'currency')
    

admin.site.register(Currency)    
admin.site.register(Product, ProductAdmin)
admin.site.register(Address)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Shopper)
admin.site.register(UniqueProduct, UniqueProductAdmin)
admin.site.register(Basket)
admin.site.register(EmailSignup)
admin.site.register(Order, OrderAdmin)
admin.site.register(Discount)
admin.site.register(Photo)
admin.site.register(Wishlist)
admin.site.register(Referee)
admin.site.register(Notify)
admin.site.register(Page, PageAdmin)
admin.site.register(Review, ReviewAdmin)



