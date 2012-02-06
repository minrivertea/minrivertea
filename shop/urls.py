from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
import views

import emails


urlpatterns = patterns('',

    url(r'^$', views.index, name="home"),
    url(r'^admin-stuff/$', views.admin_stuff, name="admin_stuff"),
    url(r'^admin-stuff/send-review-email/(\w+)$', emails._product_review_email, name="send_review_email"),
    url(r'^admin-stuff/send-reminder-email/(\w+)$', emails._order_reminder_email, name="send_reminder_email"),
    url(r'^admin-stuff/ship-it/(\w+)$', views.ship_it, name="ship_it"),
    url(r'^admin-stuff/postage-cost/(\w+)$', views.postage_cost_update, name="postage_cost_update"),
    url(r'^admin-stuff/shopper/(\w+)$', views.admin_shopper, name="admin_shopper"),
    url(r'^admin-stuff/order/(\w+)$', views.admin_order, name="admin_order"),
    url(r'^admin-stuff/send-sampler-email/(\w+)/$', emails._free_sampler_email, name="send_sampler_email"),
    url(r'^contact-us/$', views.contact_us, name="contact_us"),
    url(r'^sale/$', views.sale, name="sale"),
    url(r'^basket/$', views.basket, name="basket"),
    url(r'^basket/add/(\w+)$', views.add_to_basket, name="add_to_basket"),
    url(r'^basket/reduce/(\w+)$', views.reduce_quantity, name="reduce_quantity"),
    url(r'^basket/increase/(\w+)$', views.increase_quantity, name="increase_quantity"),
    url(r'^basket/remove/(\w+)$', views.remove_from_basket, name="remove_from_basket"),
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
    url(r'^review/thanks/$', direct_to_template, {'template': 'shop/review_thanks.html',}),
    url(r'^tea-lover/(?P<slug>[\w-]+)/$', views.tea_lover, name="tea_lover"),
    url(r'^tell-a-friend/$', views.tell_a_friend, name="tell_a_friend"),
    url(r'^not-me/$', views.not_you, name="not_you"),
    url(r'^shipping/$', views.shipping, name="shipping"),
    url(r'^currency/$', views.change_currency, name="change_currency"),
    
    # email signup specific URLs
    url(r'^email_signup/$', emails.email_signup, name="email_signup"),
    url(r'^create_email/(\w+)$', emails.create_email, name="create_email_wid"),
    url(r'^create_email/$', emails.create_email, name="create_email"),
    url(r'^send_email/(\w+)$', emails.send_email, name="send_email"),
    url(r'^email_unsubscribe/(?P<hash>[\w-]+)/$', emails.email_unsubscribe, name="email_unsubscribe"),
)

