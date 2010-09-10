from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^production/list/$', 'jade.production.views.production_list'),
    (r'^process/list/$', 'jade.production.views.process_list'),
    (r'^process/new/$', 'jade.production.views.process_new'),
    (r'^process/(?P<object_id>\d+)/delete/$', 'jade.production.views.process_delete'),
    (r'^process/(?P<object_id>\d+)/$', 'jade.production.views.process_edit'),
    (r'^job/list/$', 'jade.production.views.job_list'),
    (r'^job/new/$', 'jade.production.views.job_new'),
    (r'^job/(?P<object_id>\d+)/delete/$', 'jade.production.views.job_delete'),
    (r'^job/(?P<object_id>\d+)/$', 'jade.production.views.job_edit'),
    (r'^job/start/$', 'jade.production.views.job_start'),
    (r'^job/finish/$', 'jade.production.views.job_finish'),
    
)
