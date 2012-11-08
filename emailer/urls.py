from django.conf.urls.defaults import *

from emailer.views import *

urlpatterns = patterns('',    
    # email signup specific URLs
    url(r'^email_signup/$', email_signup, name="email_signup"),
    url(r'^send_email/(\w+)$', send_email, name="send_email"),
    url(r'^email_unsubscribe/(?P<key>[\w-]+)/$', email_unsubscribe, name="email_unsubscribe"),

    # ADMIN SPECIFIC
    url(r'^create_email/(\w+)$', create_email, name="create_email_wid"),
    url(r'^create_email/$', create_email, name="create_email"),
    url(r'^send-review-email/(\w+)$', product_review_email, name="send_review_email"),
    url(r'^send-reminder-email/(\w+)$', order_reminder_email, name="send_reminder_email"),
    url(r'^send-sampler-email/(\w+)/$', free_sampler_email, name="send_sampler_email"),
)

