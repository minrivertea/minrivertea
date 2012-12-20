from django.conf.urls.defaults import *
from django.conf import settings
import django.views.static
from django.contrib.sitemaps import FlatPageSitemap, GenericSitemap
from django.views.generic.simple import direct_to_template
from shop.models import Product, Page
from shop.views import page, category, review_tea, tea_view, make_product_feed, _changelang, germany
from shop.utils import _finder
from blog.models import BlogEntry
from blog.feeds import LatestEntriesFeed
from django.utils.translation import ugettext_lazy as _

from registration.views import register

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

# main URL patterns
urlpatterns = patterns('',
    (r'^', include('shop.urls')),
    url(r'^accounts/register/$', register, {'backend': 'shop.regbackend.SimpleBackend',}, name='registration_register'),
    (r'^accounts/', include('registration.backends.default.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^admin-stuff/', include('my_admin.urls')),
    (_(r'^blog/'), include('blog.urls')),
    (r'^captcha/', include('captcha.urls')),
    (r'^logistics/', include('logistics.urls')),
    (r'^emailer/', include('emailer.urls')),
    (r'^rosetta/', include('rosetta.urls')),
    (r'^paypal/ipn/', include('paypal.standard.ipn.urls')),
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemaps}),
    (r'^feeds/latest/$', LatestEntriesFeed()),
    (r'^robots\.txt$', direct_to_template, {'template': 'robots.txt', 'mimetype': 'text/plain'}),
    (r'^humans\.txt$', direct_to_template, {'template': 'humans.txt', 'mimetype': 'text/plain'}),
    (r'^noteaforyou/$', direct_to_template, {'template': '500.html'}),
    (r'^nomonkeys/$', direct_to_template, {'template': 'no_monkeys.html'}),
    (r'^noteaheroics/$', direct_to_template, {'template': 'no_heroics.html'}),
    (r'^noteanazis/$', direct_to_template, {'template': 'no_tea_nazis.html'}),
    
    url(r'^changelang/(?P<code>[\w-]+)/$', _changelang, name="changelang"),
    (r'^400/$', direct_to_template, {'template': '404.html'}),  
    (r'^comments/', include('django.contrib.comments.urls')), 
    
    url(r'^de/$', germany, name="germany"),
    url(r'^DE/$', germany, name="germany"),
    
    
    
    
    # test category/page resolver
    url(r'^(?P<slug>[\w-]+)/$', _finder, name="finder"),
    url(r'^(?P<z>[\w-]+)/(?P<slug>[\w-]+)/$', _finder, name="finder"),
    url(r'^(?P<z>[\w-]+)/(?P<slug>[\w-]+)/review$', review_tea, name="review_tea"),
    url(r'^(?P<y>[\w-]+)/(?P<z>[\w-]+)/(?P<slug>[\w-]+)/$', _finder, name="finder"),
    url(r'^(?P<x>[\w-]+)/(?P<y>[\w-]+)/(?P<z>[\w-]+)/(?P<slug>[\w-]+)/$', _finder, name="finder"),
    
    
    
    # urls for the products/categories
    url(r'^packages/$', category, name="packages"),
    url(r'^packages/(?P<slug>[\w-]+)/$', tea_view, name="tea_view"),
    url(r'^tasters/$', category, name="tasters"),
    url(r'^tasters/(?P<slug>[\w-]+)/$', tea_view, name="tea_view"),
    url(_(r'^teaware/$'), category, name="teaware"),
    url(_(r'^teaware/(?P<slug>[\w-]+)/$'), tea_view, name="tea_view"),
    
    url(_(r'^oolong-tea/$'), category, name="oolong_tea"),
    url(_(r'^oolong-tea/(?P<slug>[\w-]+)/$'), tea_view, name="tea_view"),

    url(_(r'^red-tea/$'), category, name="red_tea"),
    url(_(r'^red-tea/(?P<slug>[\w-]+)/$'), tea_view, name="tea_view"),

    url(_(r'^green-tea/$'), category, name="green_tea"),
    url(_(r'^green-tea/(?P<slug>[\w-]+)/$'), tea_view, name="tea_view"),

    url(_(r'^white-tea/$'), category, name="white_tea"),
    url(_(r'^white-tea/(?P<slug>[\w-]+)/$'), tea_view, name="tea_view"),

    url(_(r'^scented-tea/$'), category, name="scented_tea"),
    url(_(r'^scented-tea/(?P<slug>[\w-]+)/$'), tea_view, name="tea_view"),

    url(_(r'^tea-gifts/$'), category, name="tea_gifts"),
    url(_(r'^tea-gifts/(?P<slug>[\w-]+)/$'), tea_view, name="tea_view"),

    url(_(r'^tea-boxes/$'), category, name="tea_boxes"),
    url(_(r'^tea-boxes/(?P<slug>[\w-]+)/$'), tea_view, name="tea_view"),

    url(_(r'^teas/$'), category, name="teas"),
    url(_(r'^teas/(?P<slug>[\w-]+)/review/$'), review_tea, name="review_tea"),
    url(_(r'^teas/(?P<slug>[\w-]+)/$'), tea_view, name="tea_view"),
    
    # urls for the pages
    url(r'^(?P<x>[\w-]+)/(?P<y>[\w-]+)/(?P<z>[\w-]+)/(?P<slug>[\w-]+)/$', page, name="sub_sub_sub_page"),
    url(r'^(?P<x>[\w-]+)/(?P<y>[\w-]+)/(?P<slug>[\w-]+)/$', page, name="sub_sub_page"),
    url(r'^(?P<y>[\w-]+)/(?P<slug>[\w-]+)/$', page, name="sub_page"),
    url(r'^(?P<slug>[\w-]+)/$', page, name="page"),
    
)

# logging for SORL - have to put it here because in settings it causes import errors
import logging
from sorl.thumbnail.log import ThumbnailLogHandler
handler = ThumbnailLogHandler()
handler.setLevel(logging.ERROR)
logging.getLogger('sorl.thumbnail').addHandler(handler)


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
    (r'^modeltranslation/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT + '/modeltranslation',
        'show_indexes': settings.DEBUG}),
)
