from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
import views

from shop import emails

urlpatterns = patterns('',
    
    # custom admin URLs
    url(r'^$', views.admin_stuff, name="admin_stuff"),
    url(r'^ship-it/(\w+)$', views.ship_it, name="ship_it"),
    url(r'^postage-cost/(\w+)$', views.postage_cost_update, name="postage_cost_update"),
    url(r'^shopper/(\w+)$', views.admin_shopper, name="admin_shopper"),
    url(r'^stocks/$', views.stocks, name="stocks"),
    url(r'^stocks/(\w+)$', views.admin_product, name="admin_product"),
    url(r'^orders/$', views.orders, name="orders"),
    url(r'^orders/(\w+)$', views.admin_order, name="admin_order"),
    

    # email specific ones
    url(r'^create_email/(\w+)$', emails.create_email, name="create_email_wid"),
    url(r'^create_email/$', emails.create_email, name="create_email"),
    url(r'^send-review-email/(\w+)$', emails._product_review_email, name="send_review_email"),
    url(r'^send-reminder-email/(\w+)$', emails._order_reminder_email, name="send_reminder_email"),
    url(r'^send-sampler-email/(\w+)/$', emails._free_sampler_email, name="send_sampler_email"),
)

