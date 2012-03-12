from django.conf.urls.defaults import *
from django.conf import settings
import django.views.static
from django.contrib.sitemaps import FlatPageSitemap, GenericSitemap
from django.views.generic.simple import direct_to_template
from shop.models import Product, Page
from shop.views import page, category, review_tea, tea_view, make_product_feed
from blog.models import BlogEntry
from minriver.blog.feeds import LatestEntries

# admin urls
from django.contrib import admin
admin.autodiscover()

# for the sitemaps
products = {
    'queryset': Product.objects.filter(is_active=True),
}

blogs = {
    'queryset': BlogEntry.objects.filter(is_draft=False),	
}

pages = {
    'queryset': Page.objects.all()
}

sitemaps = {
    'pages': GenericSitemap(pages, priority=0.6),
    'products': GenericSitemap(products, priority=0.6),
    'blogs': GenericSitemap(blogs, priority=0.6),
}

# for the feeds
feeds = {
    'latest': LatestEntries,
}

# main URL patterns
urlpatterns = patterns('',
    (r'^', include('minriver.shop.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^blog/', include('minriver.blog.urls')),
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^paypal/ipn/', include('paypal.standard.ipn.urls')),
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    (r'^robots\.txt$', direct_to_template, {'template': 'robots.txt', 'mimetype': 'text/plain'}),
    (r'^humans\.txt$', direct_to_template, {'template': 'humans.txt', 'mimetype': 'text/plain'}),
    (r'^noteaforyou/$', direct_to_template, {'template': '500.html'}),
    (r'^nomonkeys/$', direct_to_template, {'template': 'no_monkeys.html'}),
    (r'^noteaheroics/$', direct_to_template, {'template': 'no_heroics.html'}),
    (r'^noteanazis/$', direct_to_template, {'template': 'no_tea_nazis.html'}),
    
    (r'^400/$', direct_to_template, {'template': '404.html'}),  
    (r'^comments/', include('django.contrib.comments.urls')), 
    
    # urls for the products/categories
    url(r'^packages/$', category, name="packages"),
    url(r'^packages/(?P<slug>[\w-]+)/$', tea_view, name="tea_view"),
    url(r'^tasters/$', category, name="tasters"),
    url(r'^tasters/(?P<slug>[\w-]+)/$', tea_view, name="tea_view"),
    url(r'^teaware/$', category, name="teaware"),
    url(r'^teaware/(?P<slug>[\w-]+)/$', tea_view, name="tea_view"),
    url(r'^teas/$', category, name="teas"),
    url(r'^teas/(?P<slug>[\w-]+)/review/$', review_tea, name="review_tea"),
    url(r'^teas/(?P<slug>[\w-]+)/$', tea_view, name="tea_view"),
    
    # URLs for the Google Product Feeds
    (r'^products\.xml$', direct_to_template, {'template': 'products.xml', 'mimetype': 'text/xml'}),
    (r'^products_us\.xml$', direct_to_template, {'template': 'products_us.xml', 'mimetype': 'text/xml'}),
    url(r'^make_product_feed/$', make_product_feed, name="make_product_feed"),
    
    # urls for the pages
    url(r'^(?P<x>[\w-]+)/(?P<y>[\w-]+)/(?P<z>[\w-]+)/(?P<slug>[\w-]+)/$', page, name="sub_sub_sub_page"),
    url(r'^(?P<x>[\w-]+)/(?P<y>[\w-]+)/(?P<slug>[\w-]+)/$', page, name="sub_sub_page"),
    url(r'^(?P<y>[\w-]+)/(?P<slug>[\w-]+)/$', page, name="sub_page"),
    url(r'^(?P<slug>[\w-]+)/$', page, name="page"),
    
    
    
    
      
)


# for the development server static files
urlpatterns += patterns('',

    # CSS, Javascript and IMages
    (r'^photos/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT + '/photos',
        'show_indexes': settings.DEBUG}),
    (r'^images/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT + '/images',
        'show_indexes': settings.DEBUG}),
    (r'^cache/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT + '/cache',
        'show_indexes': settings.DEBUG}),
    (r'^thumbs/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT + '/thumbs',
        'show_indexes': settings.DEBUG}),
    (r'^css/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT + '/css',
        'show_indexes': settings.DEBUG}),
    # for the fontface CSS trick to work
    (r'^fonts/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT + '/fonts',
        'show_indexes': settings.DEBUG}),
    (r'^js/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT + '/js',
        'show_indexes': settings.DEBUG}),
)
