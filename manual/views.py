from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    (r'^sales/$', direct_to_template, {'template': 'sales.html'})
)

