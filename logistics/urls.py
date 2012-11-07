from django.conf.urls.defaults import *
from logistics import views


urlpatterns = patterns('',
    url(r'^update-package/(\w+)$', views.update_package, name="update_package"),
    url(r'^mark-stock-as-arrived/(\w+)$', views.mark_stock_as_arrived, name="mark_stock_as_arrived"),

    url(r'^add-stocks/$', views.add_stocks, name="add_stocks"),
)

