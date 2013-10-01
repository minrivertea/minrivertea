from django.conf.urls.defaults import *
from logistics import views


urlpatterns = patterns('',
    url(r'^update-package/(\w+)$', views.update_package, name="update_package"),
    url(r'^update-stock-location/(\w+)/$', views.update_stock_location, name="update_stock_location"),
    url(r'^add-stocks/$', views.add_stocks, name="add_stocks"),
)

