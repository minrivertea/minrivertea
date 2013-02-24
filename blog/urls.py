from django.conf.urls.defaults import *
from blog import views


urlpatterns = patterns('',
    url(r'^$', views.index, name="blog_home"),
    url(r'^(?P<slug>[\w-]+)/$', views.blog_entry, name="blog_entry"),
    url(r'^/(?P<id>[\w-]+)/$', views.blog_by_id, name="blog_by_id"), # get objects by ID urls
)
