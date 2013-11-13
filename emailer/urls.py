from django.conf.urls.defaults import *

from emailer.views import *

urlpatterns = patterns('',    
    # email signup specific URLs
    url(r'^email_signup/$', email_signup, name="email_signup"),

    # ADMIN SPECIFIC
    #url(r'^create_email/(\w+)$', create_email, name="create_email_wid"),
    #url(r'^create_email/$', create_email, name="create_email"),
    url(r'^send-review-email/(\w+)$', product_review, name="product_review"),
)

