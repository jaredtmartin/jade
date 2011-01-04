from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^pull/$', 'jade.updates.views.pull', name='pull_updates'),
)

