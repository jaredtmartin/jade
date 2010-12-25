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
from django.conf import settings
from django.db import models
from django.db.models.fields import FieldDoesNotExist
from django.db.models import Q
from django.contrib.sites.models import Site
import re
def increment_string_number(number, default='1001', zfill=True):
    import string
    try:
        number=re.split("(\d*)", number)
        if number[-1]=='':
            if zfill:
                number[-2]=string.zfill(int(number[-2])+1, len(number[-2]))
            else:
                number[-2]=str(int(number[-2])+1)
        else:
            number=number[0]+'1'
        number="".join(number)
        return number
    except: return default

class CurrentMultiSiteManager(models.Manager):
    "Use this to limit objects to those associated with the current site."
    def __init__(self, field_name='site'):
        super(CurrentMultiSiteManager, self).__init__()
        self.__field_name = field_name
        self.__is_validated = False

    def get_query_set(self):
        if not self.__is_validated:
            try:
                self.model._meta.get_field(self.__field_name+'s')
            except FieldDoesNotExist:
                raise ValueError("%s couldn't find a field named %ss in %s." % \
                    (self.__class__.__name__, self.__field_name, self.model._meta.object_name))
            self.__is_validated = True
        return super(CurrentMultiSiteManager, self).get_query_set().filter(**{self.__field_name + 's__id__exact': settings.SITE_ID})
class TransactionManager(CurrentMultiSiteManager):
    def unbalanced(self):
        # TODO: Find a way to make a sql query to return all unbalanced transactions
        """
        select * from (select inventory_transaction.id, sum(value) as total from inventory_transaction left join inventory_entry on transaction_id=inventory_transaction.id group by transaction_id) as zoom where total !=0;
        """
        return []
class AccountManager(models.Manager):
    def next_number(self):
        number=super(AccountManager, self).get_query_set().all().order_by('-number')[0].number
        return increment_string_number(number)

class EntryManager(models.Manager):
    def get_query_set(self):
        return super(EntryManager, self).get_query_set().filter(site=Site.objects.get_current())
class BaseManager(models.Manager):
    def __init__(self, tipo, prefix=''):
        super(BaseManager, self).__init__()
        self.tipo=tipo
        self.prefix=prefix
    def get_query_set(self):
        return super(BaseManager, self).get_query_set().filter(tipo=self.tipo)
    def next_doc_number(self):
        try: 
            number = super(BaseManager, self).get_query_set().filter(tipo=self.tipo).order_by('-pk')[0].doc_number
            number=re.split("(\d*)", number)
            if number[-1]=='':
                number[-2]=("%%0%id" % len(number[-2])) % (int(number[-2])+1)
            return "".join(number)
        except IndexError: return "%s1001" % self.prefix
class SaleManager(BaseManager):
    def next_doc_number(self):
        try: 
            number = super(BaseManager, self).get_query_set().filter(tipo=self.tipo).order_by('-pk')[0].doc_number
            number=re.split("(\d*)", number)
            if number[-1]=='':
                number[-2]=("%%0%id" % len(number[-2])) % (int(number[-2])+1)
            return "".join(number)
        except: return "1001"    
class SettingsManager(models.Manager):
    def get(self, value):
        return super(SettingsManager, self).get_query_set().get(name=value).value
