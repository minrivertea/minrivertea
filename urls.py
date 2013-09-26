from django.conf.urls.defaults import *
from django.conf import settings
import django.views.static
from django.contrib.sitemaps import FlatPageSitemap, GenericSitemap
from django.views.generic.simple import direct_to_template
from shop.models import Product, Page
from shop.views import page, category, review_tea, review_tea_thanks, tea_view, _changelang, germany, monthly_tea_box
from blog.views import staff
from shop.utils import _finder, _internal_pages_list
from shop.sitemap import Sitemap, DESitemap
from blog.models import BlogEntry
from blog.feeds import LatestEntriesFeed
from django.utils.translation import ugettext_lazy as _
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


from registration.views import register

# admin urls
from django.contrib import admin
admin.autodiscover()

sitemap = {
    'things': Sitemap,    
}

sitemap_de = {
    'things': DESitemap,    
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
    (r'^ckeditor/', include('ckeditor.urls')),
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^logistics/', include('logistics.urls')),
    (r'^emailer/', include('emailer.urls')),
    (r'^rosetta/', include('rosetta.urls')),
    (r'^paypal/ipn/', include('paypal.standard.ipn.urls')),
    
    # SITEMAPS, FEEDS AND STATICS
    (r'^sitemap\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemap}),
    (r'^sitemap_de\.xml$', 'django.contrib.sitemaps.views.sitemap', {'sitemaps': sitemap_de}),
    (r'^feeds/latest/$', LatestEntriesFeed()),
    (r'^robots\.txt$', direct_to_template, {'template': 'robots.txt', 'mimetype': 'text/plain'}),
    (r'^humans\.txt$', direct_to_template, {'template': 'humans.txt', 'mimetype': 'text/plain'}),
    (r'^noteaforyou/$', direct_to_template, {'template': '500.html'}),
    (r'^nomonkeys/$', direct_to_template, {'template': 'no_monkeys.html'}),
    (r'^noteaheroics/$', direct_to_template, {'template': 'no_heroics.html'}),
    (r'^noteanazis/$', direct_to_template, {'template': 'no_tea_nazis.html'}),
    (r'^400/$', direct_to_template, {'template': '404.html'}),
    
    
    # random specific URLs that must appear here
    url(r'^changelang/(?P<code>[\w-]+)/$', _changelang, name="changelang"),    
    url(r'^de/$', germany, name="germany"),
    url(r'^DE/$', germany, name="germany"),
    url(r'^view_internal_pages/$', _internal_pages_list, name="internal_pages_list"),
    
    
    url(_(r'^tea-boxes/monthly-tea-box/$'), monthly_tea_box, name="monthly_tea_box"),


    # Category + Page + Tea resolver
    url(r'^(?P<slug>[\w-]+)/$', _finder, name="finder"),
    url(r'^(?P<z>[\w-]+)/(?P<slug>[\w-]+)/$', _finder, name="finder"),
    url(r'^(?P<category>[\w-]+)/(?P<slug>[\w-]+)/review/$', review_tea, name="review_tea"),
    url(r'^(?P<category>[\w-]+)/(?P<slug>[\w-]+)/review/thanks/$', review_tea_thanks, name="review_tea_thanks"),
    url(r'^(?P<y>[\w-]+)/(?P<z>[\w-]+)/(?P<slug>[\w-]+)/$', _finder, name="finder"),
    url(r'^(?P<x>[\w-]+)/(?P<y>[\w-]+)/(?P<z>[\w-]+)/(?P<slug>[\w-]+)/$', _finder, name="finder"),
    

        
    # urls for the pages
    url(r'^(?P<x>[\w-]+)/(?P<y>[\w-]+)/(?P<z>[\w-]+)/(?P<slug>[\w-]+)/$', page, name="sub_sub_sub_page"),
    url(r'^(?P<x>[\w-]+)/(?P<y>[\w-]+)/(?P<slug>[\w-]+)/$', page, name="sub_sub_page"),
    url(r'^(?P<y>[\w-]+)/(?P<slug>[\w-]+)/$', page, name="sub_page"),
    url(r'^(?P<slug>[\w-]+)/$', page, name="page"),
    
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()


# logging for SORL - have to put it here because in settings it causes import errors
import logging
from sorl.thumbnail.log import ThumbnailLogHandler
handler = ThumbnailLogHandler()
handler.setLevel(logging.ERROR)
logging.getLogger('sorl.thumbnail').addHandler(handler)

