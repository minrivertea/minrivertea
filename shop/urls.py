from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
from django.utils.translation import ugettext_lazy as _

import views
import utils

urlpatterns = patterns('',

    url(r'^$', views.index, name="home"),
    
    url(_(r'^sale/$'), views.sale, name="sale"),
    url(r'^basket/$', views.basket, name="basket"),
    url(r'^basket/add/(\w+)$', views.add_to_basket, name="add_to_basket"),
    url(r'^basket/reduce/(\w+)$', views.reduce_quantity, name="reduce_quantity"),
    url(r'^basket/increase/(\w+)$', views.increase_quantity, name="increase_quantity"),
    url(r'^basket/remove/(\w+)$', views.remove_from_basket, name="remove_from_basket"),
    
    
    # monthly order specific
    url(r'^basket/add/(?P<productID>\w+)/monthly/(?P<months>\w+)/$', views.add_to_basket_monthly, name="add_to_basket_monthly"),
    url(r'^change_monthly_frequency/(?P<months>\w+)/$', utils._change_monthly_frequency, name="change_monthly_frequency"),
    url(r'^monthly-order-save/$', views.monthly_order_save, name="monthly_order_save"),


    url(r'^contact-form-submit/$', views.contact_form_submit, name="contact_form_submit"),
    url(r'^order/step-one/$', views.order_step_one, name="order_step_one"),
    url(r'^order/confirm/$', views.order_confirm, name="order_confirm"),
    url(r'^order/complete/$', views.order_complete, name="order_complete"),
    url(r'^order/make_wishlist/$', views.order_makewishlist, name="order_makewishlist"),
    url(r'^wishlist/select_items/$', views.wishlist_select_items, name="wishlist_select_items"),
    url(r'^wishlist/submit_email/$', views.wishlist_submit_email, name="wishlist_submit_email"),
    url(r'^wishlist/(?P<hash>[\w-]+)/$', views.wishlist_url, name="wishlist_url"),
    url(r'^order/repeat/(?P<hash>[\w-]+)/$', views.order_repeat, name="order_repeat"),
    url(r'^order/(?P<hash>[\w-]+)/$', views.order_url, name="order_url"),
    url(r'^order/complete/turn-off-twitter/(\w+)$', views.turn_off_twitter, name="turn_off_twitter"),    
    url(r'^reviews/$', views.reviews, name="reviews"),
    url(r'^tell-a-friend/$', views.tell_a_friend, name="tell_a_friend"),
    url(r'^not-me/$', views.not_you, name="not_you"),
    url(r'^currency/$', utils._set_currency, name="set_currency"),
    
    # get objects by ID urls
    url(r'^page/(?P<id>[\w-]+)/$', views.page_by_id, name="page_by_id"),
    url(r'^product/(?P<id>[\w-]+)/$', views.product_by_id, name="product_by_id"),
    url(r'^category/(?P<id>[\w-]+)/$', views.category_by_id, name="category_by_id"),

    
    
)

