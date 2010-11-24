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
from django.db import models
from jade.inventory.models import Transaction, Account, Entry, make_default_account
try: from jade.inventory.models import INVENTORY_ACCOUNT
except:pass
from django.db.models.signals import post_save #pre_save, , pre_delete
from django.db.models import Q
from datetime import datetime
from jade import settings
import re
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from jade.inventory.managers import CurrentMultiSiteManager, AccountManager

if settings.PRODUCTION_EXPENSE_ACCOUNT_DATA:
    PRODUCTION_EXPENSE_ACCOUNT = make_default_account(settings.PRODUCTION_EXPENSE_ACCOUNT_DATA)
class ProductionManager(models.Manager):
    def get_query_set(self):
        return super(ProductionManager, self).get_query_set().filter(Q(tipo="Process")|Q(tipo="Job"))

class Production(Transaction):
    class Meta:
        proxy = True    
        permissions = (
            ("view_production", "Can view productions"),
        )  
    objects = ProductionManager()
    def _get_quantity(self):
        if self.entry('Inventory'): return self.entry('Inventory').quantity
        else: return None
    def _set_quantity(self, value):
        value=(value or 0)
        try:
            self.entry('Production').update('quantity', -value)
            self.entry('Inventory').update('quantity', value)
        except AttributeError: self._quantity=value
    quantity = property(_get_quantity, _set_quantity)
    def _get_active(self):
        try: return self.entry('Production').active
        except AttributeError: return self._active
    def _set_active(self, value):
        self._active=value
        [e.update('active',value) for e in self.entry_set.all()]
    active = property(_get_active, _set_active)
 ################ ################ ################  Delivered   ################ ################ ################
    def _get_delivered(self):
        try: return self.entry('Production').delivered
        except AttributeError: return self._delivered
    def _set_delivered(self, value):
        try: return [self.entry(e).update('delivered',value) for e in ['Inventory','Production']]
        except AttributeError: self._delivered=value
    delivered = property(_get_delivered, _set_delivered)
    def _get_value(self):
        return self.cost
    value=property(_get_value)
    def _get_cost(self):
        try: return self.entry('Inventory').value
        except AttributeError: return self._cost
    def _set_cost(self, value):
        dif=value-self.cost
        try:
            self.entry('Production').update('value', -value)
            self.entry('Inventory').update('value', value)
        except AttributeError:
            self._cost=value
    cost=property(_get_cost, _set_cost)
    
    def _get_item(self):
        try: return self.entry('Inventory').item
        except AttributeError: return self._item
    def _set_item(self, value):
        try: return [self.entry(e).update('item',value) for e in ['Inventory','Production']]
        except AttributeError: self._item=value
    item = property(_get_item, _set_item)
    
    def _get_serial(self):
        try: return self.entry('Inventory').serial
        except AttributeError: return self._serial    
    def _set_serial(self, value):
        try: return [self.entry(e).update('serial',value) for e in ['Inventory','Production']]
        except AttributeError: self._serial=value
    serial = property(_get_serial, _set_serial)
    
    def template(self):
        return 'production/production.html'
        
    def __init__(self, *args, **kwargs):
        self._cost = kwargs.pop('cost', 0)
        self._date = kwargs.pop('date', datetime.now())
        self._delivered = kwargs.pop('delivered', False)
        self._active = kwargs.pop('active', False)
        self._item = kwargs.pop('item', None)
        self._quantity = kwargs.pop('quantity', 0)
        self._serial = kwargs.pop('serial', None)
        super(Production, self).__init__(*args, **kwargs)
    
class ProcessManager(models.Manager):
    def get_query_set(self):
        return super(ProcessManager, self).get_query_set().filter(tipo="Process")
class Process(Production):
    def __init__(self, *args, **kwargs):
        super(Process, self).__init__(*args, **kwargs)
        self.active=False
        self.delivered=False
        self.tipo='Process'
    def template(self):
        return 'production/process.html'
    def save(self, *args, **kwargs):
        self.active=False
        self.delivered=False
        super(Process, self).save(*args, **kwargs)
    objects = ProcessManager()
    class Meta:
        proxy = True
        permissions = (
            ("view_process", "Can view processes"),
        )
    def plan(self, doc_number, times, cost):
        return Job.objects.create(
            item=self.item,
            quantity=self.quantity*times,
            cost=cost*times,
            doc_number=doc_number,
            serial="",
        )
    def next_doc_number(self):
        try:
            last_number=Job.objects.filter(doc_number__startswith=self.doc_number).order_by('-doc_number')[0].doc_number
            last_number=re.split("(\d*)", last_number)[-2]
        except: last_number='0'
        return self.doc_number+str(int(last_number)+1)

    def print_url(self):
        return '/production/process/%s/report.pdf'% self.doc_number
    def url(self):
        return '/production/process/list/?q='+unicode(self.doc_number)
        
def add_process_entries(sender, **kwargs):
    l=kwargs['instance']
    if kwargs['created']:
        l.sites.add(Site.objects.get_current())
        l.create_related_entry(
        account = PRODUCTION_EXPENSE_ACCOUNT,
        tipo = 'Production',
        value = l._cost,
        item = l._item,
        quantity=l._quantity,
        serial=l._serial,
        delivered=False,
        active=False
        )
        l.create_related_entry(
        account = INVENTORY_ACCOUNT,
        tipo = 'Inventory',
        value = - l._cost,
        item = l._item,
        quantity=-l._quantity,
        serial=l._serial,
        delivered=False,
        active=False
        )
post_save.connect(add_process_entries, sender=Process, dispatch_uid="jade.production.models:add_process_entries")
class JobManager(models.Manager):
    def get_query_set(self):
        return super(JobManager, self).get_query_set().filter(tipo="Job")
class Job(Production):
    def __init__(self, *args, **kwargs):
        super(Job, self).__init__(*args, **kwargs)
        self.tipo='Job'   
    def save(self, *args, **kwargs):
        self.tipo="Job"
        super(Job, self).save(*args, **kwargs)
    objects = JobManager()
    def _get_started(self):
        active=Entry.objects.filter(transaction__doc_number=self.doc_number, tipo='Inventory', quantity__lte=0, active=True).count()
        total=Entry.objects.filter(transaction__doc_number=self.doc_number, tipo='Inventory', quantity__lte=0).count()
        print "total = " + str(total)
        print "active = " + str(active)
        print "total==active = " + str(total==active)
        return total==active
    def _get_finished(self):
        active=Entry.objects.filter(transaction__doc_number=self.doc_number, tipo='Inventory', quantity__gt=0, active=True).count()
        total=Entry.objects.filter(transaction__doc_number=self.doc_number, tipo='Inventory', quantity__gt=0).count()
        print "total = " + str(total)
        print "active = " + str(active)
        print "total==active = " + str(total==active)
        return total==active
    def _get_start_date(self):
        if not self.started: return None
        try:
            return Entry.objects.filter(transaction__doc_number=self.doc_number, tipo='Inventory', quantity__lte=0)[0].date
        except:
            return None
    def _get_finish_date(self):
        if not self.finished: return None
        try:
            return Entry.objects.filter(transaction__doc_number=self.doc_number, tipo='Inventory', quantity__gt=0)[0].date
        except:
            return None
    def print_url(self):
        return '/production/job/%s/report.pdf'% self.doc_number
    started=property(_get_started)
    finished=property(_get_finished)
    start_date=property(_get_start_date)
    finish_date=property(_get_finish_date)
    def url(self):
        return '/production/job/list/?q='+unicode(self.doc_number)
    class Meta:
        permissions = (
            ("start_production", "Can start production"),
            ("finish_production", "Can finish production"),
            ("view_job", "Can view jobs"),
        )
        proxy = True
def add_job_entries(sender, **kwargs):
    l=kwargs['instance']
    if kwargs['created']:
        l.sites.add(Site.objects.get_current())
        l.create_related_entry(
        account = INVENTORY_ACCOUNT,
        tipo = 'Inventory',
        value = l._cost,
        item = l._item,
        quantity=l._quantity,
        serial=l._serial,
        delivered=False,
        active=False,
        )
        l.create_related_entry(
        account = PRODUCTION_EXPENSE_ACCOUNT,
        tipo = 'Production',
        value = - l._cost,
        item = l._item,
        quantity=-l._quantity,
        serial=l._serial,
        delivered=False,
        active=False,
        )
post_save.connect(add_job_entries, sender=Job, dispatch_uid="jade.production.models:add_job_entries")
