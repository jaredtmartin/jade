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
from jade.transaction.models import *
from django.views.generic import list_detail, create_update
from jade.common.views import search


urlpatterns = patterns('',
    url(r'^sales/$', list_detail.object_list,{"queryset" : Sale.objects.all()}, name='sale-list'),
#    url(r'^sales/(?P<object_id>\d+)/$', create_update.update_object, {'form_class' : SaleForm, 'extra_context':}, name='sale-detail'),
    url(r'^sales/(?P<object_id>\d+)/$', 'jade.transaction.views.sale_detail', name='sale-detail'),
    url(r'^sales/(?P<object_id>\d+)/new_sale$', 'jade.transaction.views.saleline_new', name='saleline-new'),
#    url(r'^sales/new/$', create_update.create_object, {'form_class' : SaleForm}, name='sale-detail'),
    url(r'^sales/(?P<object_id>\d+)/delete/$', create_update.delete_object, {'model' : Sale, 'post_delete_redirect':'/sales/'}, name='sale-delete'),
)

