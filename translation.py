from modeltranslation.translator import translator, TranslationOptions
from shop.models import Product, Page, Category

class ProductTranslationOptions(TranslationOptions):
    fields = (
        'name', 
        'long_name',
        'slug', 
        'description',
        'meta_title', 
        'meta_description', 
        'super_short_description', 
        'long_description',
        'body_text',
        'extra_info',
        'tag_text',
    )
    
class PageTranslationOptions(TranslationOptions):
    fields = (
        'slug', 
        'title', 
        'meta_title', 
        'meta_description', 
        'content',
    )


class CategoryTranslationOptions(TranslationOptions):
    fields = (
        'name',
        'long_title',
        'meta_description',
        'short_description',
    )

translator.register(Product, ProductTranslationOptions)
translator.register(Page, PageTranslationOptions)
translator.register(Category, CategoryTranslationOptions)


