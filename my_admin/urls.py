from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
import views

from emailer.views import *

urlpatterns = patterns('',
    
    # custom admin URLs
    url(r'^$', views.index, name="admin_home"),
    url(r'^postage-cost/(\w+)$', views.postage_cost_update, name="postage_cost_update"),
    url(r'^shopper/(\w+)$', views.admin_shopper, name="admin_shopper"),
    url(r'^stocks/$', views.stocks, name="stocks"),


    url(r'^stocks/(\w+)$', views.admin_product, name="admin_product"),
    url(r'^orders/$', views.orders, name="orders"),
    url(r'^orders/(\w+)$', views.admin_order, name="admin_order"),
    
)

