from django.conf.urls.defaults import *
from django.conf import settings
import django.views.static
from django.contrib.sitemaps import FlatPageSitemap, GenericSitemap
from django.views.generic.simple import direct_to_template
from shop.models import Product

# admin urls
from django.contrib import admin
admin.autodiscover()

# for the sitemaps
info_dict = {
    'queryset': Product.objects.filter(is_active=True),
}

sitemaps = {
    'flatpages': FlatPageSitemap,
    'products': GenericSitemap(info_dict, priority=0.6),
}

# main URL patterns
urlpatterns = patterns('',
    (r'^', include('minriver.shop.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^paypal/ipn/', include('paypal.standard.ipn.urls')),
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    (r'^robots\.txt$', direct_to_template, {'template': 'robots.txt', 'mimetype': 'text/plain'}),
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
    (r'^thumbs/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT + '/thumbs',
        'show_indexes': settings.DEBUG}),
    (r'^css/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT + '/css',
        'show_indexes': settings.DEBUG}),
    # for the fontface CSS trick to work
    (r'^css/fonts/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT + '/css/fonts',
        'show_indexes': settings.DEBUG}),
    (r'^js/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT + '/js',
        'show_indexes': settings.DEBUG}),
)
