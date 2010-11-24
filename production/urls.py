# Jade Inventory Control System
#Copyright (C) 2010  Jared T. Martin

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied account of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^production/list/$', 'jade.production.views.production_list'),
    (r'^process/list/$', 'jade.production.views.process_list'),
    (r'^process/new/$', 'jade.production.views.process_new'),
    (r'^process/(?P<object_id>\d+)/delete/$', 'jade.production.views.process_delete'),
    (r'^process/(?P<object_id>\d+)/$', 'jade.production.views.process_edit'),
    (r'^process/(?P<doc_number>\w+)/report.pdf$', 'jade.production.views.process_report'),
    (r'^job/list/$', 'jade.production.views.job_list'),
    (r'^job/new/$', 'jade.production.views.job_new'),
    (r'^job/(?P<object_id>\d+)/delete/$', 'jade.production.views.job_delete'),
    (r'^job/(?P<object_id>\d+)/$', 'jade.production.views.job_edit'),
    (r'^job/start/$', 'jade.production.views.job_start'),
    (r'^job/finish/$', 'jade.production.views.job_finish'),
    (r'^job/(?P<doc_number>\w+)/report.pdf$', 'jade.production.views.job_report'),
    
)
