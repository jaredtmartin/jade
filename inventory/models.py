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

from django.utils.translation import ugettext_lazy as _
from django.db import models
from decimal import *
from django.db.utils import DatabaseError
from datetime import datetime, timedelta
import time
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.signals import pre_save, post_save, pre_delete
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
import re
from thumbs import ImageWithThumbsField
import jade
import subprocess
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from jade.inventory.managers import *
import decimal

DEBIT=1
CREDIT=-1

def datefromstr(s, format="%m/%d/%Y"):
    return datetime.fromtimestamp(time.mktime(time.strptime(s,format)))
def dt(date):
    return datetime.fromordinal(date.toordinal())
def create_barcode(number, folder=''):
    from jade.inventory.code128 import Code128
    bar = Code128()
#    print "folder = " + str(folder)
    bar.getImage(number,50,"png", folder=settings.BARCODES_FOLDER)
def in_months(date, months):
    return date+timedelta(months*365/12)

class Tab(models.Model):
    name = models.CharField('name', max_length=32)
    url = models.CharField('url', max_length=32)
    perm = models.CharField('permission', max_length=32)
    klass = models.CharField('class', max_length=32)
    keywords = models.CharField('keywords', max_length=32,  default="", blank=True)
    def __unicode__(self):
        return self.name
    
class SettingsManager(models.Manager):
    def __call__(self, value):
        return self.get_query_set().get(name=value).value
        try: return self.get_query_set().get(name=value).value
        except Setting.DoesNotExist: return None

class Setting(models.Model):
    name = models.CharField('name', max_length=32)
    tipo = models.CharField('tipo', max_length=64)
    _value = models.CharField('_value', max_length=64)
    get=SettingsManager()
    objects=models.Manager()
    def _get_value(self):
        if self.tipo =='': return None
        elif self.tipo=='__builtin__.str': return self._value
        elif self.tipo=='__builtin__.int': return int(self._value)
        elif self.tipo=='__builtin__.bool': return bool(self._value)
        elif self.tipo=='decimal.Decimal': return decimal.Decimal(self._value)
        elif self.tipo=='__builtin__.unicode': return unicode(self._value)
        else: return eval(self.tipo).objects.get(pk=int(self._value))

    def _set_value(self, value):
        self.tipo="%s.%s" % (value.__class__.__module__,value.__class__.__name__)
        if self.tipo == '__builtin__.str' : self._value = value
        elif self.tipo == '__builtin__.int': self._value = str(value)
        elif self.tipo=='decimal.Decimal' : self._value = str(value) 
        elif self.tipo=='__builtin__.bool': 
            if value: self._value = 'True'
            else: self._value = ''
        elif self.tipo == '__builtin__.unicode': self._value = value
        elif isinstance(value, models.Model ): self._value=value.pk   
    value=property(_get_value,_set_value)
    def __unicode__(self):
        return self.name
class TransactionTipo(models.Model):
    name = models.CharField('name', max_length=32)
    obj = models.CharField('obj', max_length=64)
    def __unicode__(self):
        return self.name
        
class Report(models.Model):
    name = models.CharField(_('report'), max_length=32)
    body = models.TextField(_('body'), blank=True, default="")
    image = ImageWithThumbsField(_('image'), upload_to='uploaded_images', sizes=((125,125),(200,200)), null=True, blank=True)
    def __unicode__(self):
        return self.name
    def _get_watermark_url(self):
        if self.image: return settings.APP_LOCATION+self.image.url
        else: return None
    watermark_url=property(_get_watermark_url)

class Unit(models.Model):
    name = models.CharField(_('unit'), max_length=32)
    def __unicode__(self):
        return self.name
    def _get_hidden(self):
        return self._hidden
    def _set_hidden(self, value):
        self._hidden=value
    hidden=property(_get_hidden,_set_hidden)

class Category(models.Model):
    name = models.CharField(_('category'), max_length=32)
    def __unicode__(self):
        return self.name
    
ITEM_TYPES=(
    ('Product', _('Product')),
    ('Service', _('Service')),
    )

class ItemManager(models.Manager):
    def __init__(self, tipo=None):
        self.tipo=tipo
        super(ItemManager, self).__init__()        
#    def get_query_set(self):
#        return super(ItemManager, self).get_query_set().filter(tipo=self.tipo)
    def next_bar_code(self):
        last=Setting.objects.get(name='Last automatic barcode')
        number = increment_string_number(last.value)
        while Item.objects.filter(bar_code=number).count()>0:
            number=increment_string_number(number)
            last.value=number
            last.save()
        return number
    def find(self, q):
        query=super(ItemManager, self).get_query_set()
        if self.tipo: query=query.filter(tipo=self.tipo)
        for key in q.split():
            query=query.filter(Q(name__icontains=key) | Q(bar_code__icontains=key)|Q(description__icontains=key))
        return query
    def fetch(self, q):
        query=super(ItemManager, self).get_query_set()
        if self.tipo: query=query.filter(tipo=self.tipo)
        return query.get(Q(name=q) | Q(bar_code=q))
    def low_stock(self):
        return list(Item.objects.raw("select id from (select inventory_item.*, sum(quantity) total from inventory_item left join inventory_entry on inventory_item.id=inventory_entry.item_id where (inventory_entry.delivered=True and account_id=%i) or (inventory_entry.id is null) group by inventory_item.id) asd where (total<minimum) or (total is null and minimum>0);" % Setting.get('Inventory account').pk))

class Item(models.Model):
    """
    """
    name = models.CharField(_('name'), max_length=200, unique=True)
    bar_code = models.CharField(_('bar code'), max_length=64, blank=True)
    image = ImageWithThumbsField(_('image'), upload_to='uploaded_images', sizes=((75,75),(150,150)), null=True, blank=True)
    minimum = models.DecimalField(_('minimum'), max_digits=8, decimal_places=2, default=Decimal('0.00'), blank=True)
    maximum = models.DecimalField(_('maximum'), max_digits=8, decimal_places=2, default=Decimal('0.00'), blank=True)
    default_cost = models.DecimalField(_('default_cost'), max_digits=8, decimal_places=2, default=Decimal('0.00'), blank=True)
    location = models.CharField(_('location'), max_length=32, blank=True, default='')
    description = models.CharField(_('description'), max_length=1024, blank=True, default="")
    unit = models.ForeignKey(Unit, default=None, blank=True)
    auto_bar_code = models.BooleanField(_('automatic bar code'), default=False)
    tipo = models.CharField(_('type'), max_length=16, choices=ITEM_TYPES, default='Product')
    objects=ItemManager()
    class Meta:
        db_table = 'inventory_item'
        ordering = ('name',)
        permissions = (
            ("view_cost", "Can view costs"),
            ("view_item", "Can view items"),
        )
    def save(self, *args, **kwargs):
        try: 
            if not self.unit: 
                self.unit=Setting.get('Default unit')
        except Unit.DoesNotExist: self.unit=Setting.get('Default unit')
        super(Item, self).save(*args, **kwargs)        
        if self.bar_code != '':
            print "BLAH"
#            try: 
            if subprocess.call('ls %s/%s%s' % (settings.APP_LOCATION, settings.BARCODES_FOLDER,self.bar_code), shell=True)!=0:
                print "creating"
                create_barcode(self.bar_code, settings.BARCODES_FOLDER)
#            except:pass
    def __unicode__(self):
        return self.name
    def template(self):
        return 'inventory/item.html'
    def url(self):
        return '/inventory/item/'+unicode(self.pk)
    def barcode_url(self):
        return "/%s%s.png" % (settings.BARCODES_FOLDER, self.bar_code)
    def _get_total_cost(self):
        return Entry.objects.filter(item=self, account=Setting.get('Inventory account'), active=True).aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
    total_cost=property(_get_total_cost)
    def price(self, client=None):
        if not client: 
            try:client=Setting.get('DEFAULT_PRICE_GROUP')
            except:pass
        # fetches the price for the given client
        if type(client)==PriceGroup: group=client
        elif type(client) in (Account, Client, Vendor):group=client.price_group
        else: group=client.get_profile().price_group
        if not group: return 0
        try:
            price=Price.objects.get(item=self, group=group)
        except Price.DoesNotExist:
            price=Price.objects.create(item=self,group=group, site=Site.objects.get_current())
        return Decimal(str(round(self.cost*price.relative + price.fixed,2)))
    def discount(self, client):
        # fetches how much of a discount is given for the given client
        price=Price.objects.get(item=self, group=client.price_group)
        return Decimal(str(round(self.cost*price.relative_discount + price.fixed_discount,2)))
    def _get_stock(self):
        # How much of the item do we have in stock?
        return Entry.objects.filter(item=self, account=Setting.get('Inventory account'), delivered=True).aggregate(total=models.Sum('quantity'))['total'] or Decimal('0.00')
    stock=property(_get_stock)
    
    def _get_individual_cost(self):
        # Returns the cost of the item NOT including the cost of any linked items
        # this should be used as the cost on a sale
        stock=self.stock
        if not stock or stock==0: return self.default_cost
        return self.total_cost/stock
    individual_cost=property(_get_individual_cost)
    
    def all_linked_items(self):
        # A list of all of the items received when this one is added
        # used to make sure we don't get circulating dependancies
        items=(self,)
        for link in self.links:
            items+=link.item.all_linked_items()
        return items
        
    def _get_cost(self):
        # Returns the cost of the item and any linked items
        # this should be used in most cases
        cost=self.individual_cost
        for link in self.links:
            cost+=(link.item.cost or 0) * link.quantity 
        return cost       
    cost=property(_get_cost)
    def _get_links(self):
        # returns all of the LinkedItems for this item
        return LinkedItem.objects.filter(parent=self)
    links=property(_get_links)
    def _get_recommended(self):
        # returns the quantity recommended to purchase based on min/max
        return self.maximum-self.stock
    recommended=property(_get_recommended)
#class Item(ItemBase):
#    objects=ItemManager('Item')
#    class Meta:
#        proxy = True
#    def save(self, *args, **kwargs):
#        self.tipo='Item'
#        super(Item, self).save(*args, **kwargs)        
class Service(Item):
    objects=ItemManager('Service')
    class Meta:
        proxy = True
        permissions = (
            ("view_service", "Can view services"),
        )
    def save(self, *args, **kwargs):
        self.tipo='Service'
        super(Service, self).save(*args, **kwargs)

def create_prices_for_item(sender, **kwargs):
    if kwargs['created']:
        for group in PriceGroup.objects.all():
            Price.objects.create(item=kwargs['instance'], group=group, site=Site.objects.get_current())
post_save.connect(create_prices_for_item, sender=Item, dispatch_uid="jade.inventory.models")
post_save.connect(create_prices_for_item, sender=Service, dispatch_uid="jade.inventory.models")

class LinkedItem(models.Model):
    parent = models.ForeignKey(Item, related_name ='parent_id')
    child = models.ForeignKey(Item, related_name ='child_id')
    quantity = models.DecimalField(_('quantity'), max_digits=8, decimal_places=2, default=1)
    fixed = models.DecimalField(_('fixed'), max_digits=8, decimal_places=2, default=None)
    relative = models.DecimalField(_('relative'), max_digits=8, decimal_places=2, default=None)
    def save(self, *args, **kwargs):
        if not self.fixed: self.fixed=Setting.get('Default fixed price')
        if not self.relative: self.relative=Setting.get('Default relative price')
        super(LinkedItem, self).save(*args, **kwargs)     
    def _get_item(self):
        return self.child
    def _set_item(self, value):
        self.child=value
    item=property(_get_item)
    def _get_tipo(self):
        return "LinkedItem"
    tipo=property(_get_tipo)
class PriceGroup(models.Model):
    name = models.CharField(_('name'), max_length=32)
    def __unicode__(self):
        return self.name
def create_prices_for_price_group(sender, **kwargs):
    if kwargs['created']:
        for item in Item.objects.all():
            Price.objects.create(item=item, group=kwargs['instance'], site=Site.objects.get_current())
post_save.connect(create_prices_for_price_group, sender=PriceGroup, dispatch_uid="jade.inventory.models")

class SettingsManager(models.Manager):
    def __call__(self, value):
        return self.get_query_set().get(name=value).value
        try: return self.get_query_set().get(name=value).value
        except Setting.DoesNotExist: return None

class Setting(models.Model):
    name = models.CharField('name', max_length=32)
    tipo = models.CharField('tipo', max_length=64)
    _value = models.CharField('_value', max_length=64, blank=True, default="")
    get=SettingsManager()
    objects=models.Manager()
    def _get_value(self):
        if self.tipo =='': return None
        elif self.tipo=='__builtin__.str': return self._value
        elif self.tipo=='__builtin__.int': return int(self._value)
        elif self.tipo=='__builtin__.bool': return bool(self._value)
        elif self.tipo=='decimal.Decimal': return decimal.Decimal(self._value)
        elif self.tipo=='__builtin__.unicode': return unicode(self._value)
        else: return eval(self.tipo).objects.get(pk=int(self._value))

    def _set_value(self, value):
        self.tipo="%s.%s" % (value.__class__.__module__,value.__class__.__name__)
        if self.tipo == '__builtin__.str' : self._value = value
        elif self.tipo == '__builtin__.int': self._value = str(value)
        elif self.tipo=='decimal.Decimal' : self._value = str(value) 
        elif self.tipo=='__builtin__.bool': 
            if value: self._value = 'True'
            else: self._value = ''
        elif self.tipo == '__builtin__.unicode': self._value = value
        elif isinstance(value, models.Model ): self._value=value.pk   
    value=property(_get_value,_set_value)
    def __unicode__(self):
        return self.name

class Price(models.Model):
    class Meta:
        ordering = ('group',)
    
    def save(self, *args, **kwargs):
        if not self.site: self.site=Site.objects.get_current()
        super(Price, self).save(*args, **kwargs)
    group = models.ForeignKey(PriceGroup)
    item = models.ForeignKey(Item)
    site = models.ForeignKey(Site)#, default=Site.objects.get_current().pk
    fixed_discount = models.DecimalField(_('fixed discount'), max_digits=8, decimal_places=2, default=0)
    relative_discount = models.DecimalField(_('relative discount'), max_digits=8, decimal_places=2, default=0)
    fixed = models.DecimalField(_('fixed'), max_digits=8, decimal_places=2, default=0)
    relative = models.DecimalField(_('relative'), max_digits=8, decimal_places=2, default=1)
    def save(self, *args, **kwargs):
#        if not self.fixed: self.fixed=Setting.get('Default fixed price')
#        if not self.relative: self.relative=Setting.get('Default relative price')
        super(Price, self).save(*args, **kwargs) 
    objects = CurrentSiteManager()
    def get_tipo_display(self):
        return _("Price")
        
    def _get_tipo(self):
        return 'price'
    tipo=property(_get_tipo)
        
    def template(self):
        return 'inventory/price.html'
        
    def total(self):
        return self.item.cost*self.relative+self.fixed
        
    def __unicode__(self):
        return self.item.name + " para " + self.group.name

class Account(models.Model):
    ACCOUNT_TYPES=(
        ('Client', _('Client')),
        ('Vendor', _('Vendor')),
        ('Account', _('Account')),
        )
    MULTIPLIER_TYPES=(
        (1, _('Debito')),
        (-1, _('Credito')),
        )
    name = models.CharField(_('name'), max_length=200, unique=True)
    number = models.CharField(_('number'), max_length=32)
    multiplier = models.IntegerField(_('multiplier'), default=1, choices=MULTIPLIER_TYPES)
    tipo = models.CharField(_('type'), max_length=16, choices=ACCOUNT_TYPES)
    site = models.ForeignKey(Site)
    objects = AccountManager()
    test = models.Manager()

    class Meta:
        ordering = ('number',)
        permissions = (
            ("view_account", "Can view accounts"),
        )
    def __init__(self, *args, **kwargs):
        self.template='inventory/account.html'
        self._address =         kwargs.pop('address','')
        self._state_name =           kwargs.pop('state_name', '')
        self._country =         kwargs.pop('country', '')
        self._home_phone =      kwargs.pop('home_phone', '')
        self._cell_phone =      kwargs.pop('cell_phone', '')
        self._work_phone =      kwargs.pop('work_phone', '')
        self._fax =             kwargs.pop('fax', '')
        self._tax_number =      kwargs.pop('tax_number', '')
        self._description =     kwargs.pop('description', '')
        self._email =           kwargs.pop('email', '')
        self._registration =    kwargs.pop('registration', '')
        self._user =            kwargs.pop('user', None)
        self._tax_group =       kwargs.pop('tax_group', None)
        self._account_group =   kwargs.pop('account_group', None)
        self._price_group =     kwargs.pop('price_group', None)
        self._receipt =         kwargs.pop('receipt', Setting.get('Default receipt'))
        self._credit_days =     kwargs.pop('credit_days', Setting.get('Default credit days'))
        self._due = self._overdue = None
        super(Account, self).__init__(*args, **kwargs)
    def _get_default_tax_rate(self):
        try: return self.contact.account_group.default_tax_rate
        except: return None
    default_tax_rate=property(_get_default_tax_rate)
    def save(self, *args, **kwargs):
        if not self.tipo: self.tipo='Account'
        try:
            if not self.site: raise Site.DoesNotExist
        except Site.DoesNotExist:
            self.site=Site.objects.get_current()            
        super(Account, self).save(*args, **kwargs)
        try: self.contact.save()
        except: pass
    def __unicode__(self):
        return self.name
    def url(self):
        return '/inventory/account/'+str(self.pk)
    def _get_tax_rate(self):
        return self.tax_group.value
    tax_rate = property(_get_tax_rate)
    def _get_balance(self):
        b=Entry.objects.filter(site=Site.objects.get_current(), active=True, account__number__startswith=self.number).aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
    #        b=self.entry_set.filter(active=True).aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
        if b!=0:b=b*self.multiplier
        return b
    balance = property(_get_balance)
    def _get_tax_group(self):
        try: return self.contact.tax_group
        except: return self._tax_group
    def _set_tax_group(self, value):
        try: self.contact.tax_group = value
        except: self._tax_group= value
    tax_group=property(_get_tax_group, _set_tax_group)

    def _get_discounts_account(self):
        try: return self.account_group.discounts_account
        except: return None
    discounts_account=property(_get_discounts_account)
    def _get_receipt(self):
        try: return self.contact.receipt
        except Contact.DoesNotExist: return None
    def _set_receipt(self, value):
        try: self.contact.receipt=value
        except Contact.DoesNotExist: pass
    receipt=property(_get_receipt, _set_receipt)

    def _get_account_group(self):
        try: return self.contact.account_group
        except: return self._account_group
    def _set_account_group(self, value):
        try: self.contact.account_group = value
        except: self._account_group= value
    account_group=property(_get_account_group, _set_account_group)
    def _get_price_group(self):
        try: return self.contact.price_group
        except: return None
    def _set_price_group(self, value):
        try: self.contact.price_group = value
        except: self._price_group= value
    price_group=property(_get_price_group, _set_price_group)
    def _get_address(self):
        try: return self.contact.address
        except: return None
    def _set_address(self, value):
        try: self.contact.address = value
        except: self._address= value
    address=property(_get_address, _set_address)
    def _get_state_name(self):
        try: return self.contact.state_name
        except: return None
    def _set_state_name(self, value):
        try: 
            self.contact.state_name = value
        except: 
            self._state_name= value
    state_name=property(_get_state_name, _set_state_name)
    def _get_country(self):
        try: return self.contact.country
        except: return None
    def _set_country(self, value):
        try: self.contact.country = value
        except: self._country= value
    country=property(_get_country, _set_country)
    def _get_home_phone(self):
        try: return self.contact.home_phone
        except: return None
    def _set_home_phone(self, value):
        try: self.contact.home_phone = value
        except: self._home_phone= value
    home_phone=property(_get_home_phone, _set_home_phone)
    def _get_cell_phone(self):
        try: return self.contact.cell_phone
        except: return None
    def _set_cell_phone(self, value):
        try: self.contact.cell_phone = value
        except: self._cell_phone= value
    cell_phone=property(_get_cell_phone, _set_cell_phone)
    def _get_work_phone(self):
        try: return self.contact.work_phone
        except: return None
    def _set_work_phone(self, value):
        try: self.contact.work_phone = value
        except: self._work_phone= value
    work_phone=property(_get_work_phone, _set_work_phone)
    def _get_fax(self):
        try: return self.contact.fax
        except: return None
    def _set_fax(self, value):
        try: self.contact.fax = value
        except: self._fax= value
    fax=property(_get_fax, _set_fax)
    def _get_tax_number(self):
        try: return self.contact.tax_number
        except: return None
    def _set_tax_number(self, value):
        try: self.contact.tax_number = value
        except: self._tax_number= value
    tax_number=property(_get_tax_number, _set_tax_number)
    def _get_description(self):
        try: return self.contact.description
        except: return None
    def _set_description(self, value):
        try: self.contact.description = value
        except: self._description= value
    description=property(_get_description, _set_description)
    def _get_email(self):
        try: return self.contact.email
        except: return None
    def _set_email(self, value):
        try: self.contact.email = value
        except: self._email= value
    email=property(_get_email, _set_email)
    def _get_registration(self):
        try: return self.contact.registration
        except: return None
    def _set_registration(self, value):
        try: self.contact.registration = value
        except: self._registration= value
    registration=property(_get_registration, _set_registration)
    def _get_user(self):
        try: return self.contact.user
        except: return None
    def _set_user(self, value):
        try: self.contact.user = value
        except: self._user= value
    user=property(_get_user, _set_user)
    def _get_credit_days(self):
        try: return self.contact.credit_days
        except: return None
    def _set_credit_days(self, value):
        try: self.contact.credit_days = value
        except: self._credit_days= value
    credit_days=property(_get_credit_days, _set_credit_days)
    def _calculate_due_and_overdue(self):
        # Get a list of amounts pending and remove ones that are ==0
        trans = Transaction.objects.raw("Select inventory_transaction.id, doc_number, sum(value) total from inventory_transaction inner join inventory_entry on transaction_id=inventory_transaction.id where active=1 and account_id=%i group by doc_number"%self.id)
        self._due=[]
        for doc in trans: 
            if doc.total!=0: self._due.append(doc)
            
        # Move the ones that are overdue to the overdue list
        self._overdue=[]
        for doc in self._due:
            try: 
                first=Entry.objects.filter(transaction__doc_number=doc.doc_number, tipo='Client')[0]
                if doc.date+timedelta(days=first.account.contact.credit_days) < datetime.now():
                    self._overdue.append(doc)
            except: pass
        for trans in self._overdue:      
            self._due.remove(trans)
    def _get_due(self):
        if not self._due: self._calculate_due_and_overdue()
        return self._due
    due=property(_get_due)
    def _get_overdue(self):
        if not self._overdue: self._calculate_due_and_overdue()
        return self._overdue
    overdue=property(_get_overdue)
            
def add_contact(sender, **kwargs):
    if kwargs['created'] and kwargs['instance'].tipo in ('Client', 'Vendor'):
#        print "adding contact"
        l=kwargs['instance']
        if not l._price_group: l._price_group=Setting.get('Default price group')
        if not l._account_group: l._account_group=Setting.get('Default account group')
        if not l._receipt: l._receipt=Setting.get('Default receipt')
        c=Contact.objects.create(
            account=l, 
            credit_days=l._credit_days,
            address=l._address,
            state_name=l._state_name,
            country=l._country,
            home_phone=l._home_phone,
            cell_phone=l._cell_phone,
            work_phone=l._work_phone,
            fax=l._fax,
            tax_number=l._tax_number,
            description=l._description,
            email=l._email,
            registration=l._registration,
            user=l._user,
            price_group=l._price_group,
            account_group=l._account_group,     
            receipt=l._receipt,         
        )
class TaxRate(models.Model):
    def __init__(self, *args, **kwargs):
        super(TaxRate, self).__init__(*args, **kwargs)
        try:
            if not self.site: self.site=Site.objects.get_current()
        except:
            pass
    name = models.CharField(max_length=32)
    value = models.DecimalField(max_digits=3, decimal_places=2, default='0.00')
    sales_account = models.ForeignKey(Account, related_name = 'sales_account')
    purchases_account = models.ForeignKey(Account, related_name = 'purchases_account')
    price_includes_tax = models.BooleanField(blank=True, default=True)
    def __unicode__(self):
        return self.name 
        
#class ReceiptGroup(models.Model):
#    name = models.CharField(max_length=32)
#    receipt = models.ForeignKey(Report)
#    def __unicode__(self):
#        return self.name 
        
class AccountGroup(models.Model):
    def __init__(self, *args, **kwargs):
        super(AccountGroup, self).__init__(*args, **kwargs)
        try:
            if not self.site: self.site=Site.objects.get_current()
        except:
#            print "unable to set site on AccountGroup"
            pass
    name = models.CharField(max_length=32)
    revenue_account = models.ForeignKey(Account, related_name = 'revenue_account')
    discounts_account = models.ForeignKey(Account, related_name = 'discounts_account')
    returns_account = models.ForeignKey(Account, related_name = 'returns_account')
    default_tax_rate = models.ForeignKey(TaxRate)
    site = models.ForeignKey(Site)
    objects = CurrentSiteManager()
    def __unicode__(self):
        return self.name
class ClientManager(models.Manager):
    def default(self):
        return Setting.get('Default client')
    def next_number(self):
        number=super(ClientManager, self).get_query_set().filter(tipo="Client").order_by('-number')[0].number
        return increment_string_number(number)
    def get_or_create_by_name(self, name):
        try:
            return super(ClientManager, self).get_query_set().get(name=name)
        except:
            if name and name != '':
                if Setting.get('Autocreate clients'):
                    price_group=Setting.get('Default price group')
                    account_group=Setting.get('Default account group')
                    receipt=Setting.get('Default receipt')
                    number=Client.objects.next_number()
                    return super(ClientManager, self).create(name=name,price_group=price_group,account_group=account_group, receipt=receipt, number=number)
            else:
                return Setting.get('Default client')
    def get_query_set(self):
        return super(ClientManager, self).get_query_set().filter(tipo="Client")
class VendorManager(models.Manager):
    def default(self):
        return Setting.get('Default vendor')
    def get_query_set(self):
        return super(VendorManager, self).get_query_set().filter(tipo="Vendor")
    def next_number(self):
        number=super(VendorManager, self).get_query_set().filter(tipo="Vendor").order_by('-number')[0].number
        return increment_string_number(number)
    def get_or_create_by_name(self, name):    
        try:
            return super(VendorManager, self).get_query_set().get(name=name)
        except:
            if name and name != '':
                if Setting.get('Autocreate vendors'):
                    price_group=Setting.get('Default price group')
                    account_group=Setting.get('Default account group')
                    receipt=Setting.get('Default receipt')
                    number=Vendor.objects.next_number()
                    return super(VendorManager, self).create(name=name,price_group=price_group,account_group=account_group, receipt=receipt, number=number)
            else:
                return Setting.get('Default vendor')
class EmployeeManager(models.Manager):
    def default(self):
        return Setting.get('Default employee')
    def next_number(self):
        try: number=super(EmployeeManager, self).get_query_set().filter(tipo="Employee").order_by('-number')[0].number
        except: number='0203001'
        return increment_string_number(number)
    def get_query_set(self):
        return super(EmployeeManager, self).get_query_set().filter(tipo="Employee")

def make_default_account(data, model=Account):
    try: return model.objects.get(name=data[0])
    except model.DoesNotExist: 
#        print "couldnt find "+data[0]
        try:
            return model.objects.create(name=data[0], number=data[1], multiplier=data[2], site_id=settings.SITE_ID)
        except Site.DoesNotExist:
            print "Unable to create account because a site with id=%i does not exist" % settings.SITE_ID
    except model.MultipleObjectsReturned:
        print "We have %i %ss" % (model.objects.filter(name=data[0]).count(), data[0])
        return model.objects.filter(name=data[0])[0]
    except DatabaseError: 
        pass
#        print "pass"

#try:
try: Site.objects.filter(pk=settings.SITE_ID)
except: Site.objects.create(name='Default', id=settings.SITE_ID)
#except:
#    print "Unable to create a site to match the current site_id"

class Contact(models.Model):
    def save(self, *args, **kwargs):
        super(Contact, self).save(*args, **kwargs)
    tax_group_name = models.CharField(max_length=32)
    price_group = models.ForeignKey(PriceGroup)
    receipt = models.ForeignKey(Report)
    account_group = models.ForeignKey(AccountGroup)
    address = models.CharField(max_length=32, blank=True, default="")
    state_name = models.CharField(max_length=32, blank=True, default="")
    country = models.CharField(max_length=32, blank=True, default="")
    home_phone = models.CharField(max_length=32, blank=True, default="")
    cell_phone = models.CharField(max_length=32, blank=True, default="")
    work_phone = models.CharField(max_length=32, blank=True, default="")
    fax = models.CharField(max_length=32, blank=True, default="")
    tax_number = models.CharField(max_length=32, blank=True, default="")
    description = models.TextField(blank=True, default="")
    email = models.CharField(max_length=32, blank=True, default="")
    registration = models.CharField(max_length=32, blank=True, default="")
    user = models.ForeignKey(User, blank=True, null=True)
    account = models.OneToOneField(Account)
    credit_days=models.IntegerField(default=None)
    def save(self, *args, **kwargs):
        if not self.credit_days: self.credit_days=Setting.get('Default credit days')
        super(Contact, self).save(*args, **kwargs) 
    def _get_tax_group(self):
        return TaxGroup.objects.get(name=self.tax_group_name)
    def _set_tax_group(self, value):
        self.tax_group_name=value.name
    tax_group=property(_get_tax_group, _set_tax_group)    
    def __unicode__(self):
        return self.account.name
class Client(Account):
    def save(self, *args, **kwargs):
        self.tipo="Client"
        self.multiplier=DEBIT
        super(Client, self).save(*args, **kwargs)
    objects = ClientManager()
    class Meta:
        ordering = ('name',)
        proxy = True
        permissions = (
            ("view_client", "Can view clients"),
        )
post_save.connect(add_contact, sender=Client, dispatch_uid="jade.invenatory.models")
post_save.connect(add_contact, sender=Account, dispatch_uid="jade.inventory.models")

class Vendor(Account):
    def save(self, *args, **kwargs):
        self.tipo="Vendor"
        self.multiplier=CREDIT
        super(Vendor, self).save(*args, **kwargs)
    objects = VendorManager()
    class Meta:
        ordering = ('name',)
        proxy = True
        permissions = (
            ("view_vendor", "Can view vendors"),
        )
post_save.connect(add_contact, sender=Vendor, dispatch_uid="jade.inveantory.models")

class Employee(Account):
    def save(self, *args, **kwargs):
        self.tipo="Employee"
        self.multiplier=CREDIT
        super(Employee, self).save(*args, **kwargs)
    objects = EmployeeManager()
    class Meta:
        ordering = ('name',)
        proxy = True
        permissions = (
            ("view_employee", "Can view employees"),
        )
post_save.connect(add_contact, sender=Employee, dispatch_uid="jade.invenatory.models")

class GaranteeOffer(models.Model):
    def save(self, *args, **kwargs):
#        print "Site.objects.get_current() = " + str(Site.objects.get_current())
        try:self.site
        except Site.DoesNotExist: self.site=Site.objects.get_current()
        super(GaranteeOffer, self).save(*args, **kwargs)
    months = models.IntegerField(default=0, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'), blank=True)
    item = models.ForeignKey(Item)
    site = models.ForeignKey(Site)#, default=Site.objects.get_current().pk
    objects = CurrentSiteManager()
    def _get_tipo(self):
        return unicode("GaranteeOffer")
    tipo=property(_get_tipo)
    def __init__(self, *args, **kwargs):
        self.template='inventory/garantee_offer.html'
        super(GaranteeOffer, self).__init__(*args, **kwargs)
    def __unicode__(self):
        return 'Garantee for %i months on %s(%s)'%(self.months, self.item, str(self.price))
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    price_group = models.ForeignKey(PriceGroup)
    tabs = models.ManyToManyField(Tab)
    def __unicode__(self):
        return self.user.username
#    def _get_tabs(self, parent=None):
#        try: t=self._tabs
#        except:
#            self._tabs=[]
#            for tab in Tab.objects.all():
#                if self.user.has_perm(tab.perm):
#                    self._tabs.append(tab)
#                else:
#                    print "user doesnt have permission:%s" %tab.permission
#                    
#        return self._tabs
#    tabs=property(_get_tabs)
#    def _get_actions(self):
#        try: t=self._actions
#        except:
#            self._actions=[]
#            for action in Setting.ACTIONS:
#                if self.user.has_perms(action.permission):
#                    self._actions.append(action)
#        return self._actions
#    actions=property(_get_actions)
def add_user_profile(sender, **kwargs):
    if kwargs['created']:
        l=kwargs['instance']
        try: 
            pg=Setting.get('Default price group')
            UserProfile.objects.create(user=l, price_group=pg)
        except:pass
post_save.connect(add_user_profile, sender=User, dispatch_uid="jade.inventory.moddels")
def for_kw(self, kw): return self.get_query_set().filter(Q(keywords__icontains=kw)|Q(keywords=None)).value
UserProfile.tabs.for_kw=for_kw

class Transaction(models.Model):
    _date = models.DateTimeField(default=datetime.now())
    doc_number = models.CharField(max_length=32, default='', blank=True)
    comments = models.CharField(max_length=200, blank=True, default='')
    sites = models.ManyToManyField(Site)
    tipo = models.CharField(max_length=16)
    def __init__(self, *args, **kwargs):
        self._debit=None
        self._credit=None
        self._active = kwargs.pop('active', True)
        self.tipo = kwargs.pop('tipo', 'Transaction')
        self._debit = kwargs.pop('debit', self._debit)
        self._credit = kwargs.pop('credit', self.credit)
        self._debit_tipo = kwargs.pop('debit_tipo','Debit')
        self._credit_tipo = kwargs.pop('credit_tipo','Credit')
        self._account_tipo = kwargs.pop('account_tipo',self._debit_tipo)
        self._value_tipo = kwargs.pop('value_tipo', self._account_tipo)
        self._quantity = kwargs.pop('quantity', 0)
        self._item = kwargs.pop('item', None)
        self._serial = kwargs.pop('serial', '')
        self._active = kwargs.pop('active', True)
        self._delivered = kwargs.pop('delivered', True)
        self._value = kwargs.pop('value', Decimal('0.00'))        
        super(Transaction, self).__init__(*args, **kwargs)
        
    class Meta:
        ordering = ('-_date',)
        permissions = (
            ("view_transaction", "Can view transactions"),
        )

    def get_tipo_display(self):
        return _(self.tipo)
    def _get_date(self):
        return self._date
    def _set_date(self, value):
        self._date=value
        if len(self.entry_set.all())> 0: [e.update('date',value) for e in self.entry_set.all()]
    date=property(_get_date, _set_date)
    def balanced(self, entries=None):
        if not entries: entries=self.entry_set.all()
        s=sum([e.value for e in entries])
        if s==0: return True
        return False
    def __unicode__(self):
        return self.doc_number
    def _get_active(self):
        try: 
            for e in self.entry_set.all():
                if not e.active: return False
            return True
        except AttributeError: 
            return self._active
        
    def _set_active(self, value):
        self._active=value
        [e.update('active',value) for e in self.entry_set.all()]
    active = property(_get_active, _set_active)
    
    def create_related_entry(self, account, tipo, value=0, item=None, quantity=0, delivered=True, serial=None, count=0, cost=0, active=True, site=None):
        try: 
            if not site: site = Site.objects.get_current()
        except DatabaseError:
            pass
        e=self.entry_set.create(
            date=self.date,
            account=account,
            tipo=tipo,
            value=value,
            item=item,
            quantity=quantity,
            serial=serial,
            active=active,
            delivered=delivered,
            site=site,
            )
    def _get_subclass(self):
        try:
            if self._subclass: return self._subclass
        except: pass
        if not self.pk: return None       
        t=self.tipo
#        print "self.tipo = " + str(self.tipo)
        self._subclass=eval(TransactionTipo.objects.get(name=self.tipo).obj).objects.get(pk=self.id)
        return self._subclass
    subclass=property(_get_subclass)
    def entry(self, tipo):
        try: return self.entry_set.filter(tipo=tipo)[0]
        except: return None
        
    def update_possible_entry(self, tipo, account, value):
        if not self.pk: raise AttributeError('You must save the sale first')
        # Update the value for an entry that should only exist if the value is not 0
        if value!=0:
            if self.entry(tipo):
                self.entry(tipo).update('value', value)
            else:
                self.create_related_entry(account=account, tipo=tipo, value=value)
        elif self.entry(tipo):
            self.entry(tipo).delete()
            
    def url(self):
        return '/inventory/transactions/?q='+unicode(self.doc_number)
    def _get_garantee_expires(self):
        try: return self.garantee.expires
        except ObjectDoesNotExist: return None
    garantee_expires=property(_get_garantee_expires)
    def _get_garantee_months(self):
        try: return self.garantee.months
        except ObjectDoesNotExist: return 0
    def _set_garantee_months(self, value):
        try:
            if value==0:
                self.garantee.delete()
            else:
                self.garantee.months=value
                self.garantee.save()
        except ObjectDoesNotExist:
            if value==0: return
            self.garantee=Garantee(months=value)
            self.garantee.save()
    garantee_months = property(_get_garantee_months, _set_garantee_months)
    def _get_debit_entry(self):
        return self.entry(self._debit_tipo)
    debit_entry = property(_get_debit_entry)    
    def _get_credit_entry(self):
        return self.entry(self._credit_tipo)
    credit_entry = property(_get_credit_entry)   
    def _get_unit_value(self):
        if self.quantity != 0 and self.value !=0: return self.value / self.quantity
        else: return self.value
    unit_value = property(_get_unit_value)
        
    def _get_item(self):
        try: return self.entry(self._debit_tipo).item
        except AttributeError: return self._item
    def _set_item(self, value):
        try: [e.update('item',value) for e in self.entry_set.all()]
        except AttributeError: self._item=value
    item = property(_get_item, _set_item)
    
    def _get_serial(self):
        try: return self.entry(self._debit_tipo).serial
        except AttributeError: return self._serial
    def _set_serial(self, value):
        try: [e.update('serial',value) for e in self.entry_set.all()]
        except AttributeError: self._serial=value
    serial = property(_get_serial, _set_serial)
    
    def _get_delivered(self):
        try: return self.entry(self._debit_tipo).delivered
        except AttributeError: return self._delivered
    def _set_delivered(self, value):
        try: [e.update('delivered',value) for e in self.entry_set.all()]
        except AttributeError: self._delivered=value
    delivered = property(_get_delivered, _set_delivered)
    
    def _get_value(self):
        try: return self.entry(self._value_tipo).value
        except AttributeError: return self._value
    def _set_value(self, value):
        if not self._value_tipo == self._debit_tipo: value=value*-1
        try:
            self.entry(self._debit_tipo).update('value',value)
            self.entry(self._credit_tipo).update('value', -value)
        except: self._value = value
    value=property(_get_value, _set_value)
    def _get_debit(self):
        try: return self.entry(self._debit_tipo).account
        except AttributeError: 
            return self._debit
    def _set_debit(self, value):
        try: self.entry(self._debit_tipo).update('account', value)
        except AttributeError: 
            self._debit = value
    debit = property(_get_debit, _set_debit)
    def _get_credit(self):
        try: return self.entry(self._credit_tipo).account
        except AttributeError: return self._credit
    def _set_credit(self, value):
        try: self.entry(self._credit_tipo).update('account', value)
        except AttributeError: self._credit = value
    credit = property(_get_credit, _set_credit)
    def _get_account(self):
        try: return self.entry(self._account_tipo).account
        except AttributeError: 
            if self._account_tipo==self._credit_tipo:
                return self._credit
            else:
                return self._debit
    def _set_account(self, value):
        try: self.entry(self._account_tipo).update('account', value)
        except AttributeError: self._account = value
    account = property(_get_account, _set_account)
    def _get_quantity(self):
        try: return self.entry(self._debit_tipo).quantity
        except AttributeError: return self._quantity
    def _set_quantity(self, value):
        try:
            self.entry(self._debit_tipo).update('quantity',value)
            self.entry(self._credit_tipo).update('quantity', -value)
        except AttributeError: self._quantity=value
    quantity = property(_get_quantity, _set_quantity)
class Entry(models.Model):
#    ENTRY_TYPES = (
#        # Sale only entries
#        ('Client', 'Client'), # Debit
#        ('Revenue', 'Revenue'), # Credit
#        ('Tax', 'Tax'), # Credit
#        ('Discount', 'Discount'), # Credit
#        ('Inventory', 'Inventory'), # Debit
#        ('Expense', 'Expense'), # Debit

#        # Purchase only entries
#        ('Vendor', 'Vendor'), # Credit

#        # Count only entries
#        ('Count', 'Count'), # Debit

#        # Payment entries
#        ('Debit', 'Debit'), # Debit
#        ('Credit', 'Credit'), # Credit
#        
#        ('Production', 'Production'), # Credit
#        )
    class Meta:
        permissions = (
            ("view_entry", "Can view entries"),
            )
        ordering = ('-date',)
    objects=EntryManager()
    offsite_objects=models.Manager()
    transaction = models.ForeignKey(Transaction)
    value = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    account = models.ForeignKey(Account)
    delivered = models.BooleanField(default=True)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    item = models.ForeignKey(Item, blank=True, null=True)
    active = models.BooleanField(default=True)
    tipo = models.CharField(max_length=16)
    serial = models.CharField(max_length=32, null=True, blank=True)
    date = models.DateTimeField(default=datetime.now())
    site = models.ForeignKey(Site)
    
    def update(self, attribute, value):
        setattr(self, attribute, value)
        self.save()
                
    def __unicode__(self):
        return str(self.account.name) +"($" + str(self.value)+") " + str(self.tipo)
        
class ExtraValue(models.Model):
    name = models.CharField(max_length=32, blank=True, default="")
    value = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    transaction = models.ForeignKey(Transaction)
    def __unicode__(self):
        return str(self.name) +"(" + str(self.value)+") "
    
def add_general_entries(sender, **kwargs):
    l=kwargs['instance']
    if kwargs['created']:
        l.sites.add(Site.objects.get_current())
    
        l.create_related_entry(
        account = l._debit,
        tipo = l._debit_tipo,
        value = l._value,
        item = l._item,
        quantity=l._quantity,
        serial=l._serial,
        delivered=l._delivered,
        active=l._active,
        )
        l.create_related_entry(
        account = l._credit,
        tipo = l._credit_tipo,
        value = - l._value,
        item = l._item,
        quantity=-l._quantity,
        serial=l._serial,
        delivered=l._delivered,
        )   
post_save.connect(add_general_entries, sender=Transaction, dispatch_uid="jade.inventory.models:add_general_entries")
 ######################################################################################
 #                                 Sales
 ######################################################################################
class Action():
    def __init__(self, name, icon, onclick='', url=''):
        self.name=name
        self.icon=icon
        self.onclick=onclick
        self.url=url
class Sale(Transaction):
    class Meta:
        proxy = True
        permissions = (
            ("view_sale", "Can view sales"),
            ("view_receipt", "Can view sales"),
        )
    objects = BaseManager('Sale')
    def print_url(self):
        return '/inventory/sale/%s/receipt.pdf'% self.doc_number
    def __init__(self, *args, **kwargs):
        self._cost = kwargs.pop('cost', 0)
        self._delivered = kwargs.pop('delivered', True)
        self._client = kwargs.pop('client', Setting.get('Default client'))
        super(Sale, self).__init__(*args, **kwargs)
        self.template='inventory/sale.html'
        self.deliverable=True
        self._initial_quantity=self.quantity
        self.returnable=True
        self.extra_actions=[
            Action('Add Garantee', 'garantee.png', "addGarantee(%i,'clientgarantee'); return false;"),
            Action('Add Tax', 'coin.png', "addTax(%i,'saletax'); return false;"),
            Action('Add Discount', 'down.png', "addDiscount(%i,'salediscount'); return false;"),
            Action('Add Payment', 'garantee.png', "newTransaction('/inventory/sale/%i/pay/'); return false;"),
        ]
        self.tipo='Sale'
        
    def calculate_cost(self):
        try:
            if self.active: value=self.item.total_cost+self.cost
            else: value=self.item.total_cost
            if self.delivered: stock=self.item.stock+self.quantity
            else: stock=self.item.stock
            if stock*self.quantity == 0: return 0
            return value/stock*self.quantity
        except NameError: return 0
        except AttributeError: return 0
    def save(self, *args, **kwargs):
        try: 
            cc=self.extravalue_set.get(name='CalculatedCost')
            if cc.value==self.cost and self._initial_quantity != self.quantity:
                    self.cost = cc.value = self.calculate_cost()
                    cc.save()
        except ExtraValue.DoesNotExist: pass
        super(Sale, self).save(*args, **kwargs)        
    def _get_delivered(self):
        try: return self.entry('Client').delivered
        except AttributeError: return self._delivered
    def _set_delivered(self, value):
        try: return [self.entry(e).update('delivered',value) for e in ['Inventory','Client']]
        except AttributeError: self._delivered=value
        
    def _get_account(self):
        return self.client
        
    def _get_value(self):
        try: return -self.entry('Revenue').value
        except AttributeError: return self._value
    def _set_value(self, value):
        value=(value or 0)
        try:
            self.entry('Revenue').update('value',-value)
            self.entry('Client').update('value', value)
        except: self._value = value
        
    def _get_item(self):
        try: return self.entry('Client').item
        except AttributeError: return self._item
    def _set_item(self, value):
        try: return [self.entry(e).update('item',value) for e in ['Inventory','Client']]
        except AttributeError: self._item=value
        
    def _get_quantity(self):
        try: return self.entry('Client').quantity
        except AttributeError: return self._quantity
    def _set_quantity(self, value):
        try: 
            self.entry('Inventory').update('quantity',-value)
            self.entry('Client').update('quantity',value)
        except AttributeError: self._quantity=value
        
    def _get_serial(self):
        try: return self.entry('Client').serial
        except AttributeError: return self._serial
    def _set_serial(self, value):
        try: return [self.entry(e).update('serial',value) for e in ['Inventory','Client']]
        except AttributeError: self._serial=value
        
    def _get_client(self):
        try: return self.entry('Client').account
        except AttributeError: return self._client
    def _set_client(self, value):
        try: self.entry('Client').update('account', value)
        except AttributeError: self._client = value
        
    def _get_cost(self):
        if self.item:
            if self.item.tipo=="Service": return 0
        try: return self.entry('Expense').value
        except AttributeError: return self._cost
    def _set_cost(self, value):
        if self.item:
            if self.item.tipo=="Service": return None
        value = (value or 0)
        try:
            self.update_possible_entry('Expense', Setting.get('Expense account'), value)
            self.entry('Inventory').update('value',-value)
        except AttributeError: self._cost=value
        
    def _get_unit_cost(self):
        p=self.cost
        if self.quantity != 0 and p !=0: return p / self.quantity
        else: return p
    def _get_unit_value(self):
        if self.quantity != 0 and self.value !=0: return self.value / self.quantity
        else: return self.value
        
    delivered = property(_get_delivered, _set_delivered)
    account=property(_get_account)
    quantity = property(_get_quantity, _set_quantity)
    value=property(_get_value, _set_value)
    item = property(_get_item, _set_item)
    serial = property(_get_serial, _set_serial)
    client = property(_get_client, _set_client)
    unit_cost=property(_get_unit_cost)
    cost=property(_get_cost, _set_cost)
    unit_value = property(_get_unit_value)

def add_sale_entries(sender, **kwargs):
    if kwargs['created']:
        l=kwargs['instance']
        l.sites.add(Site.objects.get_current())
        if l.tipo=='Sale':
            account=l._client.account_group.revenue_account
            tipo='Revenue'
        else:
            account=l._client.account_group.returns_account
            tipo='Return'            
        if not l._value: l.value=0
        if not l.cost: l.cost=0
        if not l._quantity: l._quantity=0

        l.create_related_entry(
            account = account,
            tipo = tipo,
            value=l.value * -1)
        l.create_related_entry(
            account     = l._client,
            tipo        = 'Client',
            value       = l.value,
            item        = l._item,
            quantity    = l._quantity,
            serial      = l._serial,
            delivered   = l._delivered)
        l.create_related_entry(
            account     = Setting.get('Inventory account'),
            tipo        = 'Inventory',
            value       = -l.cost,
            item        = l._item,
            quantity    = -l._quantity,
            serial      = l._serial)
        if l.cost!=0:
            l.create_related_entry(
                account = Setting.get('Expense account'),
                tipo = 'Expense',
                value = l.cost)
        if kwargs['created']: ExtraValue.objects.create(transaction = kwargs['instance'], name = 'CalculatedCost', value = kwargs['instance']._cost)

post_save.connect(add_sale_entries, sender=Sale, dispatch_uid="jade.inventory.models:add_sale_entries")

class SaleReturn(Sale):
    class Meta:
        proxy = True
    objects = BaseManager('SaleReturn')
    def __init__(self, *args, **kwargs):
        super(SaleReturn, self).__init__(*args, **kwargs)
        self.template='inventory/sale_return.html'
        self.tipo='SaleReturn'
    def _get_value(self):
        try: return -self.entry('Return').value
        except AttributeError: return self._value
    def _set_value(self, value):
        value=(value or 0)
        try:
            self.entry('Return').update('value',-value)
            self.entry('Client').update('value', value)
        except: self._value = value
    value=property(_get_value, _set_value)

post_save.connect(add_sale_entries, sender=SaleReturn, dispatch_uid="jade.inventory.models")
################################################################################################
#                                   Purchases
################################################################################################
  
class Purchase(Transaction):
    class Meta:
        proxy = True
        permissions = (
            ("view_purchase", "Can view purchases"),
        )
    objects = BaseManager('Purchase','P')
    def _get_value(self):
        try: return self.entry(self._debit_tipo).value
        except AttributeError: return self._value
    def _set_value(self, value):
        try:
            self.entry(self._debit_tipo).update('value',value)
            self.entry(self._credit_tipo).update('value', -value)
        except: self._value = value
    value=property(_get_value, _set_value)
    def __init__(self, *args, **kwargs):
        self._vendor = kwargs.pop('vendor', Setting.get('Default vendor'))
        kwargs.update({
            'debit_tipo':'Inventory',
            'credit_tipo':'Vendor',
            'account_tipo':'Vendor',
            'debit':Setting.get('Inventory account'),
            'credit':self._vendor,
        })
        super(Purchase, self).__init__(*args, **kwargs)
        self.template='inventory/purchase.html'
        self._initial_value=self.value
        self._initial_quantity=self.quantity
        self.tipo='Purchase'
    def calculate_cost(self):
        try:
            if self.active: value=self.item.total_cost-self.value
            else: value=self.item.total_cost
            if self.delivered: stock=self.item.stock-self.quantity
            else: stock=self.item.stock
            if stock*self.quantity == 0: return 0
            return value/stock*self.quantity
        except NameError: return 0
        except AttributeError: return 0
    def save(self, *args, **kwargs):
        try: 
            cc=self.extravalue_set.get(name='CalculatedCost')
            if cc.value==self.value and self._initial_quantity != self.quantity:
                    self.value = cc.value = self.calculate_cost()
                    cc.save()
        except ExtraValue.DoesNotExist: pass
        super(Purchase, self).save(*args, **kwargs)
    def _get_vendor(self):
        return self.credit
    def _set_vendor(self, value):
        self.credit = value
    vendor = property(_get_vendor, _set_vendor)
    def _get_value(self):
        try: return self.entry('Inventory').value
        except AttributeError: return self._value
    def _set_value(self, value):
        value=(value or 0)
        try:
            self.entry('Vendor').update('value',-value)
            self.entry('Inventory').update('value', value)
        except: self._value = value
    value=property(_get_value, _set_value)
       
def add_purchase_extra_values(sender, **kwargs):
#    print "running funcc = "
    if kwargs['created']: 
#        print "createing extra value = "
        ExtraValue.objects.create(transaction = kwargs['instance'], name = 'CalculatedCost', value = kwargs['instance']._value)
post_save.connect(add_general_entries, sender=Purchase, dispatch_uid="jade.inventory.models")
post_save.connect(add_purchase_extra_values, sender=Purchase, dispatch_uid="jade.insventory.models")
      
class PurchaseReturn(Purchase):
    class Meta:
        proxy = True
    objects = BaseManager('PurchaseReturn','P')
    def __init__(self, *args, **kwargs):
        super(PurchaseReturn, self).__init__(*args, **kwargs)
        self.template='inventory/purchase_return.html'
        self.tipo='PurchaseReturn'
post_save.connect(add_general_entries, sender=PurchaseReturn, dispatch_uid="jade.inventory.models")
post_save.connect(add_purchase_extra_values, sender=PurchaseReturn, dispatch_uid="jade.inventory.models")

################################################################################################
#                                   CashClosing
################################################################################################
class TaxFilter():
    def __init__(self, query):
        self.query=query.filter(tipo='Tax')
    def __getitem__(self, index):
        i=self.query.filter(account__name=index).aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
        if not i==0: i=i*-1
        return i
    def _get_total(self):
        i=self.query.aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
        if not i==0: i=i*-1
        return i
    total=property(_get_total)
    def group(self, name):
        i=self.query.filter(account__name=name).aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
        if not i==0: i=i*-1
        return i
class Document():
    def __init__(self, doc_number):
        self.transactions=Transaction.objects.filter(doc_number=doc_number, tipo__startswith='Sale')
        self.lines=[]
        self.subtotal=0
        self.entries=Entry.objects.filter(transaction__doc_number=doc_number)
        for line in self.transactions.exclude(tipo='SaleTax'):
            l=line.subclass            
            self.lines.append(l)
            self.subtotal+=l.entry('Client').value
        self.doc_number=doc_number
        self.tax=TaxFilter(self.entries)
        self.total=self.subtotal+self.tax.total
        self._due =None
        self._paid_on_spot = None
        self._unpaid_on_spot = None
        self.value=self.subtotal
    
    def __repr__(self):
        return self.doc_number
    def _get_client(self):
        return self.lines[0].subclass.account
    client=property(_get_client)
    def _get_date(self):
        return self.lines[0].date
    date=property(_get_date)
    def __getitem__(self, index):
        return self.lines[index].subclass
    def _get_due(self):
        if not self._due:
            self._due = self.entries.filter(date=self.transactions[0]._date, account=self.client, tipo='Client').aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
        return self._due
    due=property(_get_due)
    def _get_paid_on_spot(self):
        if not self._paid_on_spot:
            self._paid_on_spot = (self.entries.filter(date=self.transactions[0]._date, account=self.client, tipo='Credit').aggregate(total=models.Sum('value'))['total'] or Decimal('0.00'))*-1
        return self._paid_on_spot
    paid_on_spot=property(_get_paid_on_spot)
    def _get_unpaid_on_spot(self):
        if not self._unpaid_on_spot:
            self._unpaid_on_spot = self.entries.filter(date=self.transactions[0]._date, account=self.client).aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
        return self._unpaid_on_spot
    unpaid_on_spot=property(_get_unpaid_on_spot)
    def inactive(self):
        for l in self.lines:
            if l.active: return False
        return True
class Series():
    def __init__(self, documents):
        self.documents=documents
    def append(self, document):
        self.documents.append(document)
    def __getitem__(self, index):
        return self.documents[index]    
    def __repr__(self):
        return str(self.documents)
    def __unicode__(self):
        if self.documents[0].number==self.documents[-1].number: return self.documents[0].number
        else: return "%s - %s" % (self.documents[0].number, self.documents[-1].number)
    def _get_first(self):
        return self.documents[0]
    first=property(_get_first)
    def _get_last(self):
        return self.documents[-1]
    last=property(_get_last)
    def _get_value(self):
        total=0
        for d in self.documents:
            total+=d.subtotal
        return total
    value=property(_get_value)
class CashClosing(Transaction):
    class Meta:
        proxy = True
        permissions = (
            ("view_cash_closing", "Can view cash_closings"),
        )
    objects = BaseManager('CashClosing','CT')
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'debit_tipo':'Bank',
            'credit_tipo':'Cash',
            'account_tipo':'Bank',
            'debit':Setting.get('Bank account'),
            'credit':Setting.get('Cash account'),
        })
        super(CashClosing, self).__init__(*args, **kwargs)
        self.template='inventory/cash_closing.html'
        self.tipo='CashClosing'
        self.start = datetime.date(dt(self.date))
        self.end = self.start + timedelta(days=1)
        self._documents=None
        self._sale_entries=None
        self.payments=ClientPayment.objects.filter(_date__gte=self.start, _date__lt=self.end).order_by('-_date')
        self.starting_cash=Entry.objects.filter(date__lt=self.start, account=Setting.get('Cash account')).aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
        self.ending_cash=Entry.objects.filter(date__lt=self.end, account=Setting.get('Cash account')).exclude(tipo='Cash', date=self.end).aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
        self.revenue=(Entry.objects.filter(date__gte=self.start, date__lt=self.end, tipo='Revenue').aggregate(total=models.Sum('value'))['total'] or Decimal('0.00'))*-1
        self.discount=(Entry.objects.filter(date__gte=self.start, date__lt=self.end, tipo='Discount').aggregate(total=models.Sum('value'))['total'] or Decimal('0.00'))
        self.expense=(Entry.objects.filter(date__gte=self.start, date__lt=self.end, tipo='Expense').aggregate(total=models.Sum('value'))['total'] or Decimal('0.00'))
        self.tax=(Entry.objects.filter(date__gte=self.start, date__lt=self.end, tipo='Tax').aggregate(total=models.Sum('value'))['total'] or Decimal('0.00'))*-1
        self.earnings=self.revenue+self.tax-self.discount-self.expense
        self.paymentstotal=(Entry.objects.filter(date__gte=self.start, date__lt=self.end, tipo='Debit').aggregate(total=models.Sum('value'))['total'] or Decimal('0.00'))
        self.revenue_check=self.starting_cash+self.revenue+self.tax-self.discount-self.expense-self.earnings
        self.employeepay=(Entry.objects.filter(date__gte=self.start, date__lt=self.end, tipo='Employee').aggregate(total=models.Sum('value'))['total'] or Decimal('0.00'))*-1
        self.incidentals=(Entry.objects.filter(date__gte=self.start, date__lt=self.end, tipo='Incidental').aggregate(total=models.Sum('value'))['total'] or Decimal('0.00'))
        self.cash_check=self.starting_cash+self.paymentstotal-self.employeepay-self.incidentals-self.value-self.ending_cash
        self._account_groups=None
        self._paid_sales=None
        self._unpaid_sales=None
        self._groups_by_series=None
        self._payments_by_timing=None
    def print_url(self):
#        return '/inventory/sale/%s/garantee.pdf'% self.doc_number
        return "/inventory/cashclosing/%s/report.pdf" % self.pk
    def _get_sale_entries(self):
        if not self._sale_entries:
            self._sale_entries = Entry.objects.filter(tipo='Revenue', date__gte=self.start, date__lt=self.end)
        return self._sale_entries
    sale_entries=property(_get_sale_entries)
    def create_documents_from_entries(self, entries):
        d=()
        for e in entries:
            dn=e.transaction.doc_number
            if not dn in d: d+=(dn,)
        documents=[]
        for doc in d:
            documents.append(Document(doc))
        return documents
    def _get_documents(self):
        if not self._documents:
            self._documents=self.create_documents_from_entries(self.sale_entries)
        return self._documents
    documents=property(_get_documents)
    def separate_by_paid_on_spot(self, documents):
        paid= []
        unpaid=[]
        for doc in documents:
            if doc.paid_on_spot==doc.due: 
                paid.append(doc)
            else: 
                unpaid.append(doc)
        return (paid, unpaid)
    def _get_paid_sales(self):
        if not self._paid_sales:
            self._paid_sales, self._unpaid_sales = self.separate_by_paid_on_spot(self.documents)
#        print "self._paid_sales = " + str(self._paid_sales)
#        print "self._unpaid_sales = " + str(self._unpaid_sales)
        return self._paid_sales
    paid_sales=property(_get_paid_sales)
    def _get_unpaid_sales(self):
        if not self._unpaid_sales:
            self._paid_sales, self._unpaid_sales = self.separate_by_paid_on_spot(self.documents)
        return self._unpaid_sales
    unpaid_sales=property(_get_unpaid_sales)
    def separate_by_account_group(self, documents):
        groups={}
        for doc in documents: self.update_dict_list(groups, {doc.client.account_group.name:doc})
        return groups.values()
    def _get_account_groups(self):
        if not self._account_groups:
            self._account_groups = self.separate_by_account_group(self.paid_sales)
        return self._account_groups
    account_groups=property(_get_account_groups)
    def create_series(self, documents):
        from operator import attrgetter
        documents.sort(key=attrgetter('doc_number'))
        series=[]
        last=0
        price=0
        for doc in documents:
            if series==[]:
                series.append(Series([doc]))
                l=re.split("(\d*)", doc.doc_number)
                if len(l)>1:
                    prefix=l[0:-2]
                    last=int(l[-2])
                else:
                    prefix=''
                    last=0
            else:
                x=int(re.split("(\d*)", doc.doc_number)[-2])
                if x-1==last or x==last: series[-1].append(doc)
                else: series.append(Series([doc]))
                last=x
        return series
    def _get_groups_by_series(self):
        if not self._groups_by_series:
            self._groups_by_series = []
            for group in self.account_groups:
                self._groups_by_series.append(self.create_series(group))
        return self._groups_by_series
    groups_by_series=property(_get_groups_by_series)
    def update_dict_list(self, x, y):
        for k in y.keys():
            if k in x:
                x[k].append(y[k])
            else:
                x[k]=[y[k]]
    def _get_payments_by_timing(self):
        if not self._payments_by_timing:
            self._payments_by_timing={'Early':[], 'OnTime':[],'Late':[],'Down':[],'Over':[]}
            for payment in self.payments: self.update_dict_list(self._payments_by_timing, {payment.timing:payment})
#        print "self._payments_by_timing = " + str(self._payments_by_timing)
        return self._payments_by_timing
    payments_by_timing=property(_get_payments_by_timing)    
post_save.connect(add_general_entries, sender=CashClosing, dispatch_uid="jade.inventory.models")
################################################################################################################
#                                             Payments                                                         #
################################################################################################################
class Payment(Transaction):
    class Meta:
        proxy = True
    def _get_timing(self):
        try:
            p=datetime.date(self.date)
            s=datetime.date(Sale.objects.filter(doc_number=self.doc_number)[0].date)
        except IndexError: return "Early"
        if p==s:
            s_end= s + timedelta(days=1)
            due=Entry.objects.filter(date__gte=s,date__lt=s_end, transaction__doc_number=self.doc_number, account=self.credit).aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
            if due==0: return "OnTime"
            if due>0: return "Down"
            if due<0: return "Over"
        if p<s: return "Early"
        if p>s: return "Late"
    timing = property(_get_timing)

class ClientPayment(Payment):
    class Meta:
        proxy = True
    objects = BaseManager('ClientPayment')
    
    def __init__(self, *args, **kwargs):
        newkwargs={
            'account_tipo':'Credit',
            'value_tipo':'Debit',
            'debit':Setting.get('Payments received account'),
        }
        newkwargs.update(kwargs)
        super(ClientPayment, self).__init__(*args, **newkwargs)
        self.template='inventory/client_payment.html'
        self.tipo='ClientPayment'
#    def _get_value(self):
#        try: return self.entry(self._debit_tipo).value
#        except AttributeError: return self._value
#    def _set_value(self, value):
#        try:
#            self.entry(self._debit_tipo).update('value',value)
#            self.entry(self._credit_tipo).update('value', -value)
#        except: self._value = value
#    value=property(_get_value, _set_value)
    def _get_client(self): return self.credit
    def _set_client(self, value): self.credit=value
    client=property(_get_client, _set_client)
post_save.connect(add_general_entries, sender=ClientPayment, dispatch_uid="jade.inventory.models")

class ClientRefund(ClientPayment):
    class Meta:
        proxy = True
    objects = BaseManager('ClientRefund')
    def __init__(self, *args, **kwargs):
#        kwargs.update({
#            'value_tipo':'Credit',
#        })
        super(ClientRefund, self).__init__(*args, **kwargs)
        self.tipo='ClientRefund'
post_save.connect(add_general_entries, sender=ClientRefund, dispatch_uid="jade.inventory.models")

class VendorPayment(Payment):
    class Meta:
        proxy = True
    objects = BaseManager('VendorPayment')
    
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'credit':Setting.get('Payments made account'),
        })
#        print "VendorPaymentkwargs = " + str(kwargs)
        super(VendorPayment, self).__init__(*args, **kwargs)
        self.template='inventory/vendor_payment.html'
        self.tipo='VendorPayment'
    def _get_vendor(self): return self.debit
    def _set_vendor(self, value): self.debit=value
    vendor=property(_get_vendor, _set_vendor)

post_save.connect(add_general_entries, sender=VendorPayment, dispatch_uid="jade.inventory.models")

class VendorRefund(VendorPayment):
    class Meta:
        proxy = True
    objects = BaseManager('VendorRefund')
    def __init__(self, *args, **kwargs):
#        kwargs.update({
#            'value_tipo':'Credit',
#        })
        super(VendorRefund, self).__init__(*args, **kwargs)
        self.tipo='VendorRefund'
post_save.connect(add_general_entries, sender=VendorRefund, dispatch_uid="jade.inventory.models")

################################################################################################################
#                                             Tax                                                              #
################################################################################################################

class SaleTax(Transaction):
    class Meta:
        proxy = True
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'account_tipo':'Client',
            'credit_tipo':'Tax',
            'debit_tipo':'Client',
        })
        super(SaleTax, self).__init__(*args, **kwargs)
        self.template='inventory/tax.html'
        self.tipo='SaleTax'
    def _get_client(self):
        return self.debit
    def _set_client(self, value):
        self.debit=value
    client=property(_get_client,_set_client)
post_save.connect(add_general_entries, sender=SaleTax, dispatch_uid="jade.inventory.models")
class PurchaseTax(Transaction):
    class Meta:
        proxy = True
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'account_tipo':'Vendor',
            'credit_tipo':'Vendor',
            'debit_tipo':'Tax',
            'value_tipo':'Tax',
        })
        super(PurchaseTax, self).__init__(*args, **kwargs)
        self.template='inventory/tax.html'
        self.tipo='PurchaseTax'
    def _get_vendor(self):
        return self.credit
    def _set_vendor(self, value):
        self.credit=value
    vendor=property(_get_vendor,_set_vendor)
post_save.connect(add_general_entries, sender=PurchaseTax, dispatch_uid="jade.inventory.models")
    
################################################################################################################
#                                             Discount                                                         #
################################################################################################################

class Discount(Transaction):
    class Meta:
        proxy = True
    def __init__(self, *args, **kwargs):
        super(Discount, self).__init__(*args, **kwargs)
        self.template='inventory/discount.html'
class SaleDiscount(Discount):
    class Meta:
        proxy = True
    objects = BaseManager('SaleDiscount')
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'account_tipo':'Client',
            'credit_tipo':'Client',
            'debit_tipo':'Discount',
        })
        super(SaleDiscount, self).__init__(*args, **kwargs)
        self.tipo='SaleDiscount'
    def _get_client(self):
        return self.account
    def _set_client(self, value):
        self.account=value
    client = property(_get_client, _set_client)
    def _get_value(self):
        try: return self.entry(self._account_tipo).value
        except AttributeError: return self._value
    def _set_value(self, value):
        try:
            self.entry(self._debit_tipo).update('value',-value)
            self.entry(self._credit_tipo).update('value', value)
        except: self._value = value
    value=property(_get_value, _set_value)
post_save.connect(add_general_entries, sender=SaleDiscount, dispatch_uid="jade.inventory.models")
class PurchaseDiscount(Discount):
    class Meta:
        proxy = True
    objects = BaseManager('PurchaseDiscount')
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'account_tipo':'Vendor',
            'credit_tipo':'Discount',
            'debit_tipo':'Vendor',
        })
        super(PurchaseDiscount, self).__init__(*args, **kwargs)
        self.tipo='PurchaseDiscount'
    def _get_value(self):
        try: return self.entry(self._credit_tipo).value
        except AttributeError: return -self._value
    def _set_value(self, value):
        try:
            self.entry(self._debit_tipo).update('value',-value)
            self.entry(self._credit_tipo).update('value', value)
        except: self._value = value
    value=property(_get_value, _set_value)
    def _get_vendor(self):
        return self.account
    def _set_vendor(self, value):
        self.account=value
    vendor = property(_get_vendor, _set_vendor)
post_save.connect(add_general_entries, sender=PurchaseDiscount, dispatch_uid="jade.inventory.models")
    
################################################################################################
#                                       Garantees
################################################################################################
class Garantee(Transaction):
    # Quantity is the number of months the Garantee will be active
    class Meta:
        proxy = True
    def __init__(self, *args, **kwargs):
        super(Garantee, self).__init__(*args, **kwargs)
        self._delivered=False
    def _get_expires(self):
        return self._date+timedelta(int(self.quantity)*365/12)
    expires = property(_get_expires)
    
class ClientGarantee(Garantee):
    class Meta:
        proxy = True
    objects=BaseManager('ClientGarantee')
    
    def __init__(self, *args, **kwargs):
        self._client = kwargs.pop('client', None)
        kwargs.update({
            'account_tipo':'Client',
            'debit_tipo':'Client',
            'credit_tipo':'Garantee',
            'debit':self._client,
        })
        super(ClientGarantee, self).__init__(*args, **kwargs)
        self.template='inventory/client_garantee.html'
        self.tipo='ClientGarantee'
        
    def print_url(self):
        return '/inventory/sale/%s/garantee.pdf'% self.doc_number
    def _get_client(self):
        return self.account
    def _set_client(self, value):
        self.account=value
    client = property(_get_client, _set_client)
post_save.connect(add_general_entries, sender=ClientGarantee, dispatch_uid="jade.inventory.models")

class VendorGarantee(Garantee):
    class Meta:
        proxy = True
    objects=BaseManager('VendorGarantee')
    def __init__(self, *args, **kwargs):
        self._vendor = kwargs.pop('vendor', None)
        kwargs.update({
            'account_tipo':'Vendor',
            'value_tipo':'Garantee',
            'debit_tipo':'Garantee',
            'credit_tipo':'Vendor',
            'credit':self._vendor,
            'debit':Setting.get('Expense account'),
        })
        super(VendorGarantee, self).__init__(*args, **kwargs)
        self.template='inventory/vendor_garantee.html'
        self.tipo='VendorGarantee'
    def _get_vendor(self):
        return self.account
    def _set_vendor(self, value):
        self.account=value
    vendor = property(_get_vendor, _set_vendor)
post_save.connect(add_general_entries, sender=VendorGarantee, dispatch_uid="jade.inventory.models")
################################################################################################
#                                             Equity
################################################################################################
class Equity(Transaction):
    class Meta:
        proxy = True
    objects=BaseManager('Equity','Q')
    
    def __init__(self, *args, **kwargs):
        self._client = kwargs.pop('client', None)
        kwargs.update({
            'account_tipo':'Cash',
            'debit_tipo':'Cash',
            'credit_tipo':'Equity',
            'debit':Setting.get('Cash account'),
            'credit':Setting.get('Equity account'),
        })
        super(Equity, self).__init__(*args, **kwargs)
        self.template='inventory/equity.html'
        self.tipo='Equity'
post_save.connect(add_general_entries, sender=Equity, dispatch_uid="jade.inventory.models")
class Expense(Transaction):
    class Meta:
        proxy = True
    objects=BaseManager('Expense','X')
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'account_tipo':'Incidental',
            'debit_tipo':'Incidental',
            'credit_tipo':'Cash',
            'debit':Setting.get('Expense account'),
            'credit':Setting.get('Cash account'),
        })
        super(Expense, self).__init__(*args, **kwargs)
        self.template='inventory/expense.html'
        self.tipo='Expense'
post_save.connect(add_general_entries, sender=Expense, dispatch_uid="jade.inventory.models")
class Anullment(Transaction):
    class Meta:
        proxy = True
    objects=BaseManager('Anullment','N')
    def __init__(self, *args, **kwargs):
#        kwargs.update({
#            'account_tipo':'Anullment',
#            'debit_tipo':'Anullment',
#            'credit_tipo':'Anullment',
#            'debit':Setting.get('Expense account'),
#            'credit':Setting.get('Cash account'),
#        })
        super(Anullment, self).__init__(*args, **kwargs)
        self.template='inventory/anullment.html'
        self.tipo='Anullment'
class EmployeePay(Transaction):
    class Meta:
        proxy = True
    objects=BaseManager('EmployeePay','E')
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'account_tipo':'Employee',
            'debit_tipo':'Employee',
            'credit_tipo':'Cash',
            'credit':Setting.get('Cash account'),
            'debit':Setting.get('Employees account'),
        })
        super(EmployeePay, self).__init__(*args, **kwargs)
        self.template='inventory/employeepay.html'
        self.tipo='EmployeePay'
post_save.connect(add_general_entries, sender=EmployeePay, dispatch_uid="jade.inventory.models")

class Work(Transaction):
    class Meta:
        proxy = True
    objects=BaseManager('Work','W')
    def __init__(self, *args, **kwargs):
        kwargs.update({
            'account_tipo':'Employee',
            'debit_tipo':'Expense',
            'value_tipo':'Expense',
            'credit_tipo':'Employee',
            'credit':Setting.get('Employees account'),
            'debit':Setting.get('Expense account'),
        })
        super(Work, self).__init__(*args, **kwargs)
        self.template='inventory/work.html'
        self.tipo='Work'
        
post_save.connect(add_general_entries, sender=Work, dispatch_uid="jade.inventory.models")



################################################################################################
#                                          Counts
################################################################################################
class CountManager(BaseManager):
    def __init__(self):
        super(CountManager,self).__init__('Count')
    def post_as_sale(self, pk):
        sale=None
        count=self.get(pk=pk)
        if (count.count or 0) - count.item.stock + count.quantity<0:
            quantity=((count.count or 0) - count.item.stock + count.quantity)*-1
            if quantity==0: price = count.item.price(Setting.get('Default client'))
            else: price = count.item.price(Setting.get('Default client')) * quantity
            sale=Sale(pk=count.pk,
            doc_number=count.doc_number,
            client=Setting.get('Default client'), 
            quantity=quantity,
            item=count.item,
            cost=count.unit_cost * quantity,
            value=price)
            count.delete()
            sale.save()
            try:
                if not sale.errors: sale.errors={}
            except:
                sale.errors={}
            return sale
        else:
            count.errors={'Quantity':[u'Only counts with quantities lower than current stock levels can be converted into sales.',]}
            return count
class Count(Transaction):
    class Meta:
        proxy = True
        permissions = (
            ("view_count", "Can view counts"),
            ("post_count", "Can post counts"),
            ("post_count_sale", "Can post counts as sales"),
        )
    def print_url(self):
        return '/inventory/count/%s/sheet.pdf'% self.doc_number
    objects = CountManager()
    def __init__(self, *args, **kwargs):
        self._unit_cost = kwargs.pop('unit_cost', 0)
        self._count = kwargs.pop('count', None)
        kwargs.update({
            'account_tipo':'Inventory',
            'debit_tipo':'Inventory',
            'credit_tipo':'Expense',
            'debit':Setting.get('Inventory account'),
            'credit':Setting.get('Counts expense account'),
        })
        super(Count, self).__init__(*args, **kwargs)
        self.template='inventory/count.html'
        self.tipo='Count'
    def __unicode__(self):
        msg='Count'
        if str(self.doc_number)!='': msg+=" #"+self.doc_number
        try:
            if self.item: msg +=' of ' + self.item.name
        except:
            pass
        return msg
    def _get_unit_cost(self):
        try:
            return self.extravalue_set.get(name = 'UnitCost').value
        except ObjectDoesNotExist: 
            return self._unit_cost
    def _set_unit_cost(self, value):
        try:
            ev=self.extravalue_set.get(name = 'UnitCost')
            ev.value=value
            ev.save()
        except ObjectDoesNotExist: 
            self._unit_cost = value
    unit_cost=property(_get_unit_cost, _set_unit_cost)
    def _get_count(self):
        try:
            return self.extravalue_set.get(name = 'Count').value
        except ObjectDoesNotExist: 
            return self._count
    def _set_count(self, value):
        try:
            ev=self.extravalue_set.get(name = 'Count')
            ev.value=value
            ev.save()
        except ObjectDoesNotExist: 
            self._count = value
    count=property(_get_count, _set_count)
    def _get_posted(self):
        return (self._delivered and self._active)
    def _set_posted(self, value):
        self.active=True
        self.delivered=True
    posted=property(_get_posted, _set_posted)
    def post(self):
        if not self.item: 
            self.errors={'Item':[u'cannot be empty.',]}
            return False
        self.quantity = self.count - self.item.stock + self.quantity
        self.value = self.unit_cost * self.quantity
        self.save()
        self.errors={}
        return True
def add_count_details(sender, **kwargs):
#    print "running"
    if kwargs['created']:
        l=kwargs['instance']
        ExtraValue.objects.create(transaction = kwargs['instance'], name = 'Count', value = kwargs['instance']._count)
        ExtraValue.objects.create(transaction = kwargs['instance'], name = 'UnitCost', value = kwargs['instance']._unit_cost)
post_save.connect(add_count_details, sender=Count, dispatch_uid="jade.inventory.models")
post_save.connect(add_general_entries, sender=Count, dispatch_uid="jade.inventory.moddels")



class Transfer(Transaction):
    objects = BaseManager('Transfer','T')
    #    Entry Name             Account     Site
    #    SourceInventory        Inventory   A
    #    SourceTransfer         Transfer    A
    #    DestInventory          Inventory   B
    #    DestTransfer           Transfer    B
    class Meta:
        proxy = True
        permissions = (
            ("view_transfer", "Can view transfers"),
            ("view_site", "Can view sites"),
        )
    
    def __init__(self, *args, **kwargs):
        self._cost = kwargs.pop('cost', 0)
        self._unit_cost = kwargs.pop('unit_cost', 0)
        self._date = kwargs.pop('date', datetime.now())
        self._delivered = kwargs.pop('delivered', True)
        self._active = kwargs.pop('active', True)
        self._item = kwargs.pop('item', None)
        self._quantity = kwargs.pop('quantity', 0)
        self._serial = kwargs.pop('serial', None)
        self._account = kwargs.pop('account', None)
        super(Transfer, self).__init__(*args, **kwargs)
        self.template='inventory/transfer.html'
        self.tipo='Transfer'
    
    def __unicode__(self):
        msg='Transfer'
        if str(self.doc_number)!='': msg+=" #"+self.doc_number
        return msg
    
    def entry(self, tipo):
        try: return Entry.offsite_objects.filter(transaction=self, tipo=tipo)[0]
        except: return None        
    def _get_value(self):
        return self.cost
    def _set_value(self, value):
        self.cost=value
    def _get_active(self):
        try: return self.local_inventory_entry.active
        except Entry.DoesNotExist: return self._active
    def _set_active(self, value):
        self._active=value
        [e.update('active',value) for e in Entry.offsite_objects.filter(transaction=self)]
    def _get_delivered(self):
        try: return self.local_inventory_entry.delivered
        except Entry.DoesNotExist: return self._delivered
    def _set_delivered(self, value):
        try: 
            [e.update('delivered',value) for e in self.entry_set.all()]
        except AttributeError: self._delivered=value
        
    def _get_item(self):
        try: return self.local_inventory_entry.item
        except Entry.DoesNotExist: return self._item
    def _set_item(self, value):
        try: 
            [e.update('item',value) for e in Entry.offsite_objects.filter(transaction=self)]
        except AttributeError: self._item=value
        
    def _get_quantity(self):
        try: 
            v = self.local_inventory_entry.quantity
            #if self.source != Site.objects.get_current(): v=-v
            return v
        except Entry.DoesNotExist: return self._quantity
    def _set_quantity(self, value):
        try:            
            self.local_inventory_entry.update('quantity', value)
            self.local_transfer_entry.update('quantity', -value)
            self.remote_inventory_entry.update('quantity', -value)
            self.remote_transfer_entry.update('quantity', value)
        except AttributeError: self._quantity=value
    def _get_serial(self):
        try: return self.local_inventory_entry.serial
        except Entry.DoesNotExist: return self._serial
    def _set_serial(self, value):
        try: 
            [e.update('serial',value) for e in Entry.offsite_objects.filter(transaction=self)]
        except AttributeError: self._serial=value
    def _get_account(self):
        return self._get_remote_inventory_entry().site
    def _set_account(self, value):
        try:
            remote=self._get_remote_inventory_entry()
            if value!=remote.site:
                remote.site=value
                remote.save()
        except Entry.DoesNotExist:
            self._account=value
    def _get_source(self):
        try: return self.entry('SourceInventory').site
        except AttributeError: return self._source
    def _set_source(self, value):
        try: 
            if value!=self.entry('SourceInventory').site:
                self.entry('SourceInventory').update('site', value)
                self.entry('SourceTransfer').update('site', value)
        except AttributeError: self._source = value
    def _get_dest(self):
        try: return self.entry('DestInventory').site
        except AttributeError: return self._dest
    def _set_dest(self, value):
        try: 
            if value!=self.entry('DestInventory').site:
                self.entry('DestInventory').update('site', value)
                self.entry('DestTransfer').update('site', value)
        except AttributeError: self._dest = value
    
    def _get_local_inventory_entry(self):
        return Entry.offsite_objects.filter(transaction=self, site=Site.objects.get_current(), account=Setting.get('Inventory account')).get()
    local_inventory_entry=property(_get_local_inventory_entry)
    
    def _get_local_transfer_entry(self):
        return Entry.offsite_objects.filter(transaction=self, site=Site.objects.get_current(), account=Setting.get('Transfer account')).get()
    local_transfer_entry=property(_get_local_transfer_entry)
    
    def _get_remote_inventory_entry(self):
        return Entry.offsite_objects.filter(transaction=self, account=Setting.get('Inventory account')).exclude(site=Site.objects.get_current()).get()
    remote_inventory_entry=property(_get_remote_inventory_entry)
    
    def _get_remote_transfer_entry(self):
        return Entry.offsite_objects.filter(transaction=self, account=Setting.get('Transfer account')).exclude(site=Site.objects.get_current()).get()
    remote_transfer_entry=property(_get_remote_transfer_entry)
    
    def _get_cost(self):
        try: 
            return self.local_inventory_entry.value
        except Entry.DoesNotExist: return self._cost
    def _set_cost(self, value):
        try:
            self.local_inventory_entry.update('value', value)
            self.local_transfer_entry.update('value', -value)
            self.remote_inventory_entry.update('value', -value)
            self.remote_transfer_entry.update('value', value)
        except AttributeError:
            self._cost=value
    def _get_unit_cost(self):
        p=self.cost
        if self.quantity != 0 and p !=0: return p / self.quantity
        else: return p
    delivered = property(_get_delivered, _set_delivered)
    item = property(_get_item, _set_item)
    active = property(_get_active, _set_active)
    value=property(_get_value, _set_value)
    quantity = property(_get_quantity, _set_quantity)
    serial = property(_get_serial, _set_serial)
    account = property(_get_account, _set_account)
    source = property(_get_source, _set_source)
    dest = property(_get_dest, _set_dest)
    cost=property(_get_cost, _set_cost)
    unit_cost=property(_get_unit_cost)
            
def add_transfer_entry(sender, **kwargs):
    if kwargs['created']:
        l=kwargs['instance']
        l.sites.add(l._account)
        l.sites.add(Site.objects.get_current())
      
        l.create_related_entry(
            account = Setting.get('Inventory account'),
            tipo = 'SourceInventory',
            value = l._cost,
            item = l._item,
            quantity = l._quantity,
            serial = l._serial,
            delivered = l._delivered,
            site = Site.objects.get_current(),
        )
        l.create_related_entry(
            account = Setting.get('Transfer account'),
            tipo = 'SourceTransfer',
            value = -l._cost,
            item = l._item,
            quantity = -l._quantity,
            serial = l._serial,
            delivered = l._delivered,
            site = Site.objects.get_current(),
        )
        l.create_related_entry(
            account = Setting.get('Inventory account'),
            tipo = 'DestInventory',
            value = -l._cost,
            item = l._item,
            quantity = -l._quantity,
            serial = l._serial,
            delivered = l._delivered,
            site = l._account,
        )
        l.create_related_entry(
            account = Setting.get('Transfer account'),
            tipo = 'DestTransfer',
            value = l._cost,
            item = l._item,
            quantity=l._quantity,
            serial=l._serial,
            delivered=l._delivered,
            site = l._account,
        )    
post_save.connect(add_transfer_entry, sender=Transfer, dispatch_uid="jade.inventory.moddels")
