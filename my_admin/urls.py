from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
import views

from emailer.views import *

urlpatterns = patterns('',
    
    # custom admin URLs
    url(r'^$', views.index, name="admin_home"),
    url(r'^orders/order/(\w+)/mark_order_as_paid$', views.mark_order_as_paid, name="mark_order_as_paid"),
    url(r'^postage-cost/(\w+)$', views.postage_cost_update, name="postage_cost_update"),
    url(r'^shopper/(\w+)$', views.admin_shopper, name="admin_shopper"),
    url(r'^stats/$', views.stats, name="admin_stats"),
    url(r'^stocks/$', views.stocks, name="admin_stocks"),
    url(r'^stocks/(\w+)$', views.admin_product, name="admin_product"),
    url(r'^export/$', views.export, name="export"),
    url(r'^orders/$', views.orders, name="admin_orders"),
    url(r'^orders/(\w+)$', views.admin_order, name="admin_order"),
    url(r'^export-emails/$', views.export_emails, name="export_emails"),
    url(r'^print_packing_slip/(\w+)$', views.print_packing_slip, name="print_packing_slip"),
)

