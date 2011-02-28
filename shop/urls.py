from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
import views


urlpatterns = patterns('',

    url(r'^$', views.index, name="home"),
    url(r'^admin-stuff/$', views.admin_stuff, name="admin_stuff"),
    url(r'^admin-stuff/ship-it/(\w+)$', views.ship_it, name="ship_it"),
    url(r'^admin-stuff/shopper/(\w+)$', views.admin_shopper, name="admin_shopper"),
    url(r'^teas/$', views.teas, name="teas"),
    url(r'^teas/(?P<slug>[\w-]+)/$', views.tea_view, name="tea_view"),
    url(r'^basket/$', views.basket, name="basket"),
    url(r'^basket/add/(\w+)$', views.add_to_basket, name="add_to_basket"),
    url(r'^basket/reduce/(\w+)$', views.reduce_quantity, name="reduce_quantity"),
    url(r'^basket/increase/(\w+)$', views.increase_quantity, name="increase_quantity"),
    url(r'^basket/remove/(\w+)$', views.remove_from_basket, name="remove_from_basket"),
    url(r'^order/check-details/$', views.order_check_details, name="order_check_details"),
    url(r'^order/confirm/$', views.order_confirm, name="order_confirm"),
    url(r'^order/complete/$', views.order_complete, name="order_complete"),    
    url(r'^order/update-discount$', views.update_discount, name="update_discount"),
    url(r'^photos/$', views.photos, name="photos"),
    url(r'^tea-lover/(?P<slug>[\w-]+)/$', views.tea_lover, name="tea_lover"),
    url(r'^tell-a-friend/$', views.tell_a_friend, name="tell_a_friend"),
    url(r'^not-me/$', views.not_you, name="not_you"),
)

