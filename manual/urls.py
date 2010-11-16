from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    (r'^sales/$', direct_to_template, {'template': 'manual/sales.html'}),
    (r'^items/$', direct_to_template, {'template': 'manual/items.html'}),
    (r'^home/$', direct_to_template, {'template': 'manual/home.html'}),
    (r'^accounts/$', direct_to_template, {'template': 'manual/accounts.html'}),
    (r'^transactions/$', direct_to_template, {'template': 'manual/transactions.html'}),
    (r'^purchases/$', direct_to_template, {'template': 'manual/purchases.html'}),
)

