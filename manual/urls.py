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
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('',
    (r'^sales/$', direct_to_template, {'template': 'manual/sales.html'}),
    (r'^items/$', direct_to_template, {'template': 'manual/items.html'}),
    (r'^home/$', direct_to_template, {'template': 'manual/home.html'}),
    (r'^accounts/$', direct_to_template, {'template': 'manual/accounts.html'}),
    (r'^transactions/$', direct_to_template, {'template': 'manual/transactions.html'}),
    (r'^counts/$', direct_to_template, {'template': 'manual/counts.html'}),
    (r'^production/$', direct_to_template, {'template': 'manual/production.html'}),
    (r'^$', direct_to_template, {'template': 'manual/home.html'}),
)

