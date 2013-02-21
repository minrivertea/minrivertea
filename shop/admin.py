from shop.models import *
from django.contrib import admin

class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_filter = ('category',)
    fieldsets = (
        ('Name', {
            'fields': ('name', 'name_de', 'long_name', 'long_name_de', 'slug', 'slug_en', 'slug_de', 'meta_title', 'meta_title_de')
        }),
        ('Descriptions', {
            'fields': ('description_en', 'description_de', 'meta_description_en', 'meta_description_de', 'super_short_description_en', 'super_short_description_de', 'body_text_en', 'body_text_de', 'long_description_en', 'long_description_de', 'extra_info_en', 'extra_info_de',
            'map_image', 'map_caption_en', 'map_caption_de', 'farm_image', 'farm_caption_en', 'farm_caption_de')
        }),
        ('Images', {
            'fields': ('image', 'image_2', 'image_2_caption', 'image_3', 'image_3_caption',
                'image_4', 'image_4_caption', 'image_5', 'image_5_caption',)
        }),
        ('Others', {
            'fields': ('category', 'is_featured', 'is_active', 'tag_text', 'tag_color', 'list_order',)
        }),
    )

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
   
class OrderAdmin(admin.ModelAdmin):
    list_display = ('invoice_id', 'is_paid', 'owner', 'notes',)

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'email', 'is_published')
    
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'parent')

class UniqueProductAdmin(admin.ModelAdmin):
    list_display = ('parent_product', 'weight', 'price', 'is_sale_price', 'is_active', 'currency')
    list_filter = ('is_active', 'currency')
    

admin.site.register(Currency)    
admin.site.register(Product, ProductAdmin)
admin.site.register(Address)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Shopper)
admin.site.register(UniqueProduct, UniqueProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Discount)
admin.site.register(Wishlist)
admin.site.register(Page, PageAdmin)
admin.site.register(Review, ReviewAdmin)



