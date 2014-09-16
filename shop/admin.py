from shop.models import *
from django.contrib import admin

# DEFINES AN INLINE PRICE THING TO GO IN THE PRODUCT ADMIN
class PriceInline(admin.TabularInline):
    model = UniqueProduct
    extra = 1

    def change_view(self, request, object_id, form_url='.', extra_context={}):
        object = self.model.objects.get(identifier=object_id)
        extra_context = {'price': object,}
        return super(PriceInline, self).change_view(request, object_id, form_url, extra_context)



class ProductAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'slug', 'category', 'is_active')
    list_filter = ('category',)
    fieldsets = (
        ('Name', {
            'fields': ('name','long_name', 'slug', 'meta_title')
        }),
        ('Descriptions', {
            'fields': ('description', 'meta_description','body_text', 'long_description' )
        }),
        ('Images', {
            'fields': ('image', 'image_2', 'image_2_caption', 'image_3', 'image_3_caption',
                'image_4', 'image_4_caption', 'image_5', 'image_5_caption',)
        }),
        ('Others', {
            'fields': ('category', 'is_featured', 'is_active', 'tag_text', 'tag_color', 'list_order',)
        }),
    )
    
    inlines = [PriceInline,]
    





class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'parent_category', 'slug')
   
class OrderAdmin(admin.ModelAdmin):
    list_display = ('invoice_id', 'owner', 'notes',)
    filter_horizontal = ('items',)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'email', 'is_published')
    
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'parent')

class DiscountAdmin(admin.ModelAdmin):
    list_display = ('discount_code', 'name', 'discount_value')

class UniqueProductAdmin(admin.ModelAdmin):
    list_display = ('parent_product', 'weight', 'price', 'sale_price', 'is_active', 'currency')
    list_filter = ('is_active', 'currency')


class DealAdmin(admin.ModelAdmin):
    filter_horizontal = ('product_group_1', 'product_group_2', 'product_group_3' )

admin.site.register(Currency)    
admin.site.register(Deal, DealAdmin)    
admin.site.register(NotifyOutOfStock)    
admin.site.register(Product, ProductAdmin)
admin.site.register(Address)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Shopper)
admin.site.register(UniqueProduct, UniqueProductAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Discount, DiscountAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Review, ReviewAdmin)



