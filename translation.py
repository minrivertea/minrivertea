from modeltranslation.translator import translator, TranslationOptions
from shop.models import Product, Page, Category, UniqueProduct
from blog.models import BlogEntry

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
        'map_caption',
        'farm_caption',
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
        'slug',
        'long_title',
        'meta_description',
        'short_description',
    )

class UniqueProductTranslationOptions(TranslationOptions):
    fields = (
        'description',   
    )

class BlogEntryTranslationOptions(TranslationOptions):
    fields = (
        'slug',
        'title',
        'content',
        'summary',   
    )


translator.register(Product, ProductTranslationOptions)
translator.register(Page, PageTranslationOptions)
translator.register(Category, CategoryTranslationOptions)
translator.register(UniqueProduct, UniqueProductTranslationOptions)
translator.register(BlogEntry, BlogEntryTranslationOptions)



