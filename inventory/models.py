from django.utils.translation import ugettext_lazy as _
from django.db import models
from decimal import *
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.signals import pre_save, post_save, pre_delete
from jade import settings
#from settings import settings.BARCODES_FOLDER, settings.DEFAULT_CLIENT_NAME, settings.DEFAULT_VENDOR_NAME, settings.DEFAULT_FIXED_PRICE,settings.DEFAULT_RELATIVE_PRICE, settings.PAYMENTS_RECEIVED_ACCOUNT_NAME, settings.PAYMENTS_MADE_ACCOUNT_NAME, settings.APP_LOCATION, settings.DEFAULT_PRICE_GROUP_NAME, settings.DEFAULT_TAX_GROUP_NAME, settings.AUTOCREATE_CLIENTS, settings.AUTOCREATE_VENDORS, settings.DEFAULT_UNIT_NAME, settings.BASE_TABS,settings.DEFAULT_CREDIT_DAYS
from django.core.exceptions import ObjectDoesNotExist
import re
from thumbs import ImageWithThumbsField
import jade
import subprocess
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from jade.inventory.managers import CurrentMultiSiteManager

"""

mysqldump -uroot -pThaneM3dia --add-drop-table --no-data simplejade | grep '^DROP TABLE IF EXISTS `inventory'| mysql -uroot -pThaneM3dia simplejade
./manage.py syncdb

"""

DEBIT=1
CREDIT=-1

def create_barcode(number, folder=''):
    from jade.inventory.code128 import Code128
    bar = Code128()
    bar.getImage(number,50,"png", folder=settings.BARCODES_FOLDER)
def in_months(date, months):
    return date+timedelta(months*365/12)
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
try: DEFAULT_UNIT=Unit.objects.get(name=settings.DEFAULT_UNIT_NAME)
except:DEFAULT_UNIT=None
def increment_string_number(number):
    number=re.split("(\d*)", number)
    if number[-1]=='':
        number[-2]=str(int(number[-2])+1)
    else:
        number=number[0]+'1'
    number="".join(number)
    return number
class ItemManager(models.Manager):
    def next_bar_code(self):
        try:
            number=super(ItemManager, self).get_query_set().all().order_by('-bar_code')[0].bar_code
            number=increment_string_number(number)
            while Item.objects.filter(bar_code=number).count()>0:
#                print "Item.objects.filter(bar_code=number).count()=" + str(Item.objects.filter(bar_code=number).count())
                number=increment_string_number(number)
            return number
        except: return '1'
    def find(self, q):
        return super(ItemManager, self).get_query_set().filter(Q(name__icontains=q) | Q(bar_code__icontains=q)|Q(description__icontains=q))
    def fetch(self, q):
        return super(ItemManager, self).get_query_set().get(Q(name=q) | Q(bar_code=q))
class Item(models.Model):
    """
    """
    name = models.CharField(_('name'), max_length=200)
    bar_code = models.CharField(_('bar code'), max_length=64, blank=True)
    image=ImageWithThumbsField(_('image'), upload_to='uploaded_images', sizes=((75,75),(150,150)), null=True, blank=True)
    minimum = models.DecimalField(_('minimum'), max_digits=8, decimal_places=2, default=Decimal('0.00'), blank=True)
    maximum = models.DecimalField(_('maximum'), max_digits=8, decimal_places=2, default=Decimal('0.00'), blank=True)
    location = models.CharField(_('location'), max_length=32, blank=True, default='')
    description = models.CharField(_('description'), max_length=1024, blank=True, default="")
    unit = models.ForeignKey(Unit, default=DEFAULT_UNIT, blank=True)
#    cost = models.DecimalField(_('cost'), max_digits=8, decimal_places=2, default=Decimal('0.00'), blank=True)
    auto_bar_code = models.BooleanField(_('automatic bar code'), default=False)
    tipo = models.CharField(_('type'), max_length=16, choices=ITEM_TYPES, default='Product')
    objects=ItemManager()
    class Meta:
        ordering = ('name',)
        permissions = (
            ("view_cost", "Can view costs"),
            ("view_item", "Can view items"),
        )
    def __unicode__(self):
        return self.name
    def template(self):
        return 'inventory/item.html'
    def url(self):
        return '/inventory/item/'+str(self.pk)
    def barcode_url(self):
        return "/%s%s.png" % (settings.BARCODES_FOLDER, self.bar_code)
    def _get_total_cost(self):
#        return self.cost*self.stock
        return Entry.objects.filter(item=self, account=INVENTORY_ACCOUNT, active=True).aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
    total_cost=property(_get_total_cost)
    def price(self, client):
        if type(client)==PriceGroup: group=client
        elif type(client) in (Account, Client, Vendor, Branch):group=client.price_group
        else: group=client.get_profile().price_group
        if not group: return 0
        try:
            price=Price.objects.get(item=self, group=client)
        except Price.DoesNotExist:
            price=Price.objects.create(item=self,group=group, site=Site.objects.get_current())
        return Decimal(str(round(self.cost*price.relative + price.fixed,2)))
    def discount(self, client):
        price=Price.objects.get(item=self, group=client.price_group)
        return Decimal(str(round(self.cost*price.relative_discount + price.fixed_discount,2)))
    def _get_stock(self):
        return Entry.objects.filter(item=self, account=INVENTORY_ACCOUNT, delivered=True).aggregate(total=models.Sum('quantity'))['total'] or Decimal('0.00')
    stock=property(_get_stock)
    def _get_cost(self):
        stock=abs(self.stock)
        if not stock or stock==0: stock=1
        return self.total_cost/stock
    cost=property(_get_cost)


def create_prices_for_product(sender, **kwargs):
    if kwargs['instance'].bar_code != '':
        if subprocess.call('ls %s%s' % (settings.BARCODES_FOLDER,kwargs['instance'].bar_code), shell=True)!=0:
            create_barcode(kwargs['instance'].bar_code, settings.BARCODES_FOLDER)
    if kwargs['created']:
        for group in PriceGroup.objects.all():
            Price.objects.create(item=kwargs['instance'], group=group, site=Site.objects.get_current())
post_save.connect(create_prices_for_product, sender=Item, dispatch_uid="jade.inventory.models")

class PriceGroup(models.Model):
    name = models.CharField(_('name'), max_length=32)
    def __unicode__(self):
        return self.name
def create_prices_for_price_group(sender, **kwargs):
    if kwargs['created']:
        for item in Item.objects.all():
            Price.objects.create(item=item, group=kwargs['instance'], site=Site.objects.get_current())
post_save.connect(create_prices_for_price_group, sender=PriceGroup, dispatch_uid="jade.inventory.models")

class Price(models.Model):
    group = models.ForeignKey(PriceGroup)
    item = models.ForeignKey(Item)
    site = models.ForeignKey(Site)
    fixed_discount = models.DecimalField(_('fixed discount'), max_digits=8, decimal_places=2, default=0)
    relative_discount = models.DecimalField(_('relative discount'), max_digits=8, decimal_places=2, default=0)
    fixed = models.DecimalField(_('fixed'), max_digits=8, decimal_places=2, default=settings.DEFAULT_FIXED_PRICE)
    relative = models.DecimalField(_('relative'), max_digits=8, decimal_places=2, default=settings.DEFAULT_RELATIVE_PRICE)
    
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
        ('Branch', _('Branch')),
        ('Simple', _('Simple')),
)
    MULTIPLIER_TYPES=(
        (1, _('Debito')),
        (-1, _('Credito')),
)
    name = models.CharField(_('name'), max_length=200)
    number = models.CharField(_('number'), max_length=32)
    multiplier = models.IntegerField(_('multiplier'), default=1, choices=MULTIPLIER_TYPES)
    tipo = models.CharField(_('type'), max_length=16, choices=ACCOUNT_TYPES)
    site = models.ForeignKey(Site)
    objects = CurrentSiteManager()


    class Meta:
        ordering = ('number',)
    def __init__(self, *args, **kwargs):
        self.template='inventory/account.html'
#        self._number =          kwargs.pop('number','')
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
        self._price_group =     kwargs.pop('price_group', None)
        self._due = self._overdue = None
        super(Account, self).__init__(*args, **kwargs)
    def save(self, *args, **kwargs):
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
        b=Entry.objects.filter(active=True, account__number__startswith=self.number).aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
#        b=self.entry_set.filter(active=True).aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
        if b!=0:b=b*self.multiplier
        return b
    balance = property(_get_balance)
    def _get_tax_group(self):
        try: return self.contact.tax_group
        except: return None
    def _set_tax_group(self, value):
        try: self.contact.tax_group = value
        except: self._tax_group= value
    tax_group=property(_get_tax_group, _set_tax_group)
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
#        print "setting state_name to" + value
        try: 
            self.contact.state_name = value
#            print "saved to contact"
        except: 
            self._state_name= value
#            print "saved to mem"
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
                    self._due.remove(doc)
            except: pass
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
        l=kwargs['instance']
#        print "l.id=" + str(l.id)
        print "making contact"
        print "l._address = " + str(l._address)
        print "l._registration = " + str(l._registration)
        Contact.objects.create(
            account=l, 
            credit_days=settings.DEFAULT_CREDIT_DAYS,
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
            tax_group=l._tax_group,           
        )
class TaxGroup(models.Model):
    name = models.CharField(max_length=200)
    value = models.DecimalField(max_digits=3, decimal_places=2, default='0.00')
    revenue_account = models.ForeignKey(Account, related_name = 'revenue_account_id')
    sales_tax_account = models.ForeignKey(Account, related_name = 'sales_tax_account_id')
    purchases_tax_account = models.ForeignKey(Account, related_name = 'purchases_tax_account_id')
    discounts_account = models.ForeignKey(Account, related_name = 'discounts_account_id')
    returns_account = models.ForeignKey(Account, related_name = 'returns_account_id')
    price_includes_tax = models.BooleanField(blank=True, default=True)
    
    def __unicode__(self):
        return self.name

class ClientManager(models.Manager):
    def default(self):
        return super(ClientManager, self).get_query_set().get(name=settings.DEFAULT_CLIENT_NAME)
    def get_or_create_by_name(self, name):
        
        try:
            return super(ClientManager, self).get_query_set().get(name=name)
        except:
            if name and name != '':
                if settings.AUTOCREATE_CLIENTS:
                    price_group=PriceGroup.objects.get(name=settings.DEFAULT_PRICE_GROUP_NAME)
                    tax_group=TaxGroup.objects.get(name=settings.DEFAULT_TAX_GROUP_NAME)
                    return super(ClientManager, self).create(name=name,price_group=price_group,tax_group=tax_group)
            else:
                return super(ClientManager, self).get_query_set().get(name=settings.DEFAULT_CLIENT_NAME)
    def get_query_set(self):
        return super(ClientManager, self).get_query_set().filter(tipo="Client")
class Client(Account):
    def save(self, *args, **kwargs):
        self.tipo="Client"
        self.multiplier=DEBIT
        super(Client, self).save(*args, **kwargs)
    objects = ClientManager()
    class Meta:
        proxy = True
        permissions = (
            ("view_client", "Can view clients"),
        )
post_save.connect(add_contact, sender=Client, dispatch_uid="jade.inventory.models")
post_save.connect(add_contact, sender=Account, dispatch_uid="jade.inventory.models")
class VendorManager(models.Manager):
    def default(self):
        return super(VendorManager, self).get_query_set().get(name=settings.DEFAULT_VENDOR_NAME)
    def get_query_set(self):
        return super(VendorManager, self).get_query_set().filter(tipo="Vendor")
    def get_or_create_by_name(self, name):        
#        print "geting and creating"
#        print "name=" + str(name)
        try:
            return super(VendorManager, self).get_query_set().get(name=name)
        except:
            if name and name != '':
                if settings.AUTOCREATE_VENDORS:
                    price_group=PriceGroup.objects.get(name=settings.DEFAULT_PRICE_GROUP_NAME)
                    tax_group=TaxGroup.objects.get(name=settings.DEFAULT_TAX_GROUP_NAME)
                    return super(VendorManager, self).create(name=name,price_group=price_group,tax_group=tax_group)
            else:
                return super(VendorManager, self).get_query_set().get(name=settings.DEFAULT_VENDOR_NAME)
class Vendor(Account):
    def save(self, *args, **kwargs):
        self.tipo="Vendor"
        self.multiplier=CREDIT
        super(Vendor, self).save(*args, **kwargs)
    objects = VendorManager()
    class Meta:
        proxy = True
        permissions = (
            ("view_vendor", "Can view vendors"),
        )
post_save.connect(add_contact, sender=Vendor, dispatch_uid="jade.inventory.models")
class BranchManager(models.Manager):
    def get_query_set(self):
        return super(BranchManager, self).get_query_set().filter(tipo="Branch")
class Branch(Account):
    def save(self, *args, **kwargs):
        self.tipo="Branch"
        self.multiplier=DEBIT
        super(Branch, self).save(*args, **kwargs)
    objects = BranchManager()
    class Meta:
        proxy = True
        permissions = (
            ("view_branch", "Can view branches"),
        )
class Contact(models.Model):
    tax_group = models.ForeignKey(TaxGroup, blank=True, null=True)
    price_group = models.ForeignKey(PriceGroup, blank=True, null=True)
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
    credit_days=models.IntegerField(default=settings.DEFAULT_CREDIT_DAYS)
    def __unicode__(self):
        return self.account.name
try:
#    DEFAULT_SALES_TAX_ACCOUNT=Account.objects.get(name=settings.DEFAULT_SALES_TAX_ACCOUNT_NAME)
    INVENTORY_ACCOUNT = Account.objects.get(name=settings.INVENTORY_ACCOUNT_NAME)
    EXPENSE_ACCOUNT = Account.objects.get(name=settings.EXPENSE_ACCOUNT_NAME)
    CASH_ACCOUNT = Account.objects.get(name=settings.CASH_ACCOUNT_NAME)
#    DEFAULT_REVENUE_ACCOUNT = Account.objects.get(name=settings.DEFAULT_REVENUE_ACCOUNT_NAME)
#    DEFAULT_RETURNS_ACCOUNT = Account.objects.get(name=settings.DEFAULT_RETURNS_ACCOUNT_NAME)
#    DEFAULT_DISCOUNTS_ACCOUNT = Account.objects.get(name=settings.DEFAULT_DISCOUNTS_ACCOUNT_NAME)
    PAYMENTS_RECEIVED_ACCOUNT = Account.objects.get(name=settings.PAYMENTS_RECEIVED_ACCOUNT_NAME)
    PAYMENTS_MADE_ACCOUNT = Account.objects.get(name=settings.PAYMENTS_MADE_ACCOUNT_NAME)
    DEFAULT_CLIENT = Account.objects.get(name=settings.DEFAULT_CLIENT_NAME)
    DEFAULT_VENDOR = Account.objects.get(name=settings.DEFAULT_VENDOR_NAME)
except:
    print " ####################### Not Creating Constants ####################### "##################################################
# Transaction##################################################

TRANSACTION_TYPES=(
        ('Sale', 'Sale'),
        ('Purchase', 'Purchase'),
        ('Count', 'Count'),
        ('Transfer', 'Transfer'),
        ('ClientPayment', 'Payment'),
        ('VendorPayment', 'Payment.'),
        ('ClientRefund', 'Refund'),
        ('VendorRefund', 'Refund.'),
        ('ClientGarantee', 'Garantee'),
        ('VendorGarantee', 'Garantee.'),
        ('SaleReturn', 'Return'),
        ('PurchaseReturn', 'Return.'),
        ('Process', 'Process'),
        ('Job', 'Job'),
)
class TransactionManager(CurrentMultiSiteManager):
    def unbalanced(self):
        # TODO: Find a way to make a sql query to return all unbalanced transactions
        """
        select * from (select inventory_transaction.id, sum(value) as total from inventory_transaction left join inventory_entry on transaction_id=inventory_transaction.id group by transaction_id) as zoom where total !=0;
        """
        return []

class Transaction(models.Model):
    objects = TransactionManager()
    _date = models.DateTimeField(default=datetime.now())
    doc_number = models.CharField(max_length=32, default='', blank=True)
    comments = models.CharField(max_length=200, blank=True, default='')
    sites = models.ManyToManyField(Site)
    tipo = models.CharField(max_length=16, choices=TRANSACTION_TYPES)
 ################ ################ ################  Date   ################ ################ ################
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
    def create_related_entry(self, account, tipo, value=0, item=None, quantity=0, delivered=True, serial=None, count=0, cost=0, active=True):#cost_left=0, quantity_left=0, 
        e=self.entry_set.create(
        account=account,
        tipo=tipo,
        value=value,
        item=item,
        quantity=quantity,
        serial=serial,
        active=active,
        delivered=delivered,
#        cost_left=cost_left,
#        quantity_left=quantity_left
        )
    def _get_subclass(self):
        try:
            if self._subclass: return self._subclass
        except: pass
        if not self.pk: return None
        print "self.tipo = " + str(self.tipo)
        
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
        return '/inventory/transactions/?q='+self.doc_number
 ################ ################ ################  Garantee   ################ ################ ################
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

class Entry(models.Model):
    """
    """
    ENTRY_TYPES = (
        # Sale only entries
        ('Client', 'Client'), # Debit
        ('Revenue', 'Revenue'), # Credit
        ('Tax', 'Tax'), # Credit
        ('Discount', 'Discount'), # Credit
        ('Inventory', 'Inventory'), # Debit
        ('Expense', 'Expense'), # Debit

        # Purchase only entries
        ('Vendor', 'Vendor'), # Credit

        # Count only entries
        ('Count', 'Count'), # Debit

        # Payment entries
        ('Debit', 'Debit'), # Debit
        ('Credit', 'Credit'), # Credit

        # Garantee entries
        ('Garanteed', 'Garanteed'), # Debit
        ('Garanteer', 'Garanteer'), # Credit
        
        
        ('Production', 'Production'), # Credit
    )
    class Meta:
        permissions = (
            ("view_entry", "Can view entries"),
        )
        ordering = ('-date',)
    transaction = models.ForeignKey(Transaction)
    value = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    account = models.ForeignKey(Account)
    delivered = models.BooleanField(default=True)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default='0.00')
    item = models.ForeignKey(Item, blank=True, null=True)
    active = models.BooleanField(default=True)
    tipo = models.CharField(max_length=16, choices=ENTRY_TYPES)
    serial = models.CharField(max_length=32, null=True, blank=True)
    date = models.DateTimeField(default=datetime.now())
    sites = models.ManyToManyField(Site)
    objects = CurrentMultiSiteManager()
    
    def update(self, attribute, value):
        setattr(self, attribute, value)
        self.save()
        
    def __unicode__(self):
        return str(self.account.name) +"($" + str(self.value)+") " + str(self.tipo)
        

 ######################################################################################
 # Sales
 ######################################################################################


class SaleManager(models.Manager):
    def get_query_set(self):
        return super(SaleManager, self).get_query_set().filter(tipo="Sale")
    def next_doc_number(self):
        try:
            number=super(SaleManager, self).get_query_set().filter(tipo="Sale").order_by('-pk')[0].doc_number
            number=re.split("(\d*)", number)
            if number[-1]=='':
                number[-2]=str(int(number[-2])+1)
            number="".join(number)
        except: number="1001"
        return number
        
    def find(self):
        return super(SaleManager, self).raw("SELECT inventory_transaction.*, prices.value price FROM inventory_transaction left join (select transaction_id, sum(value) value from inventory_entry where tipo='Client' and active=1) as prices on transaction_id=inventory_transaction.id")

class Sale(Transaction):
    class Meta:
        proxy = True
        permissions = (
            ("view_sale", "Can view sales"),
            ("view_receipt", "Can view sales"),
        )
    objects = SaleManager()
    def print_url(self):
        return '/inventory/sale/%s/receipt.pdf'% self.doc_number

    def __init__(self, *args, **kwargs):
        self.template='inventory/sale.html'
        self._price = kwargs.pop('price',0)
        self._cost = kwargs.pop('cost', 0)
        self._date = kwargs.pop('date', datetime.now())
        self._delivered = kwargs.pop('delivered', True)
        self._tax = kwargs.pop('tax', 0)
        self._active = kwargs.pop('active', True)
        self._discount = kwargs.pop('discount', 0)
        self._item = kwargs.pop('item', None)
        self._quantity = kwargs.pop('quantity', 0)
        self._serial = kwargs.pop('serial', None)
        self._client = kwargs.pop('client', DEFAULT_CLIENT)
        super(Sale, self).__init__(*args, **kwargs)
        self.tipo='Sale'
        
 ################ ################ ################  Active   ################ ################ ################
    def _get_active(self):
        try: return self.entry('Client').active
        except AttributeError: return self._active
    def _set_active(self, value):
        self._active=value
        [e.update('active',value) for e in self.entry_set.all()]
    active = property(_get_active, _set_active)
 ################ ################ ################  Delivered   ################ ################ ################
    def _get_delivered(self):
        try: return self.entry('Client').delivered
        except AttributeError: return self._delivered
    def _set_delivered(self, value):
        try: return [self.entry(e).update('delivered',value) for e in ['Inventory','Client']]
        except AttributeError: self._delivered=value
    delivered = property(_get_delivered, _set_delivered)
 ################ ################ ################  Account   ################ ################ ################

    def _get_account(self):
        return self.client
    account=property(_get_account)
 ################ ################ ################  Value   ################ ################ ################

    def _get_value(self):
        return self.charge
    value=property(_get_value)

 ################ ################ ################  Item   ################ ################ ################

    def _get_item(self):
        try: return self.entry('Client').item
        except AttributeError: return self._item
    def _set_item(self, value):
        try: return [self.entry(e).update('item',value) for e in ['Inventory','Client']]
        except AttributeError: self._item=value
    item = property(_get_item, _set_item)

 ################ ################ ################  Quantity   ################ ################ ################
    def _get_quantity(self):
        try: return self.entry('Client').quantity
        except AttributeError: return self._quantity
    def _set_quantity(self, value):
        value=(value or 0)
        try:
            if not self.pk: raise AttributeError('You must save the sale first')
            self.entry('Client').update('quantity', value)
            i=self.entry('Inventory')
            # Update the value for an entry that should only exist if there is a cost or a quantity
            ### NOTE: Always save quantity before item or maybe the item might get dropped!
            # TODO: Fixme
            if value!=0 and not i:
                self.create_related_entry(account=INVENTORY_ACCOUNT, tipo='Inventory', quantity=-value)
            elif i:
                if value!=0 or i.value!=0:
                    i.update('quantity', -value)
                else:
                    i.delete()
                    self._item=None
                    self._quantity=0
        except AttributeError: self._quantity=value
    quantity = property(_get_quantity, _set_quantity)
 ################ ################ ################  Serial  ################ ################ ################
    def _get_serial(self):
        try: return self.entry('Client').serial
        except AttributeError: return self._serial
    def _set_serial(self, value):
        try: return [self.entry(e).update('serial',value) for e in ['Inventory','Client']]
        except AttributeError: self._serial=value
    serial = property(_get_serial, _set_serial)
 ################ ################ ################  Client  ################ ################ ################
    def _get_client(self):
        try: return self.entry('Client').account
        except AttributeError: return self._client
    def _set_client(self, value):
        try: self.entry('Client').update('account', value)
        except AttributeError: self._client = value
    client = property(_get_client, _set_client)
 ################ ################ ################  Cost  ################ ################ ################
    def _get_cost(self):
        try: return self.entry('Expense').value
        except AttributeError: return self._cost
    def _set_cost(self, value):
        value = (value or 0)
        try:
            if not self.pk: raise AttributeError('You must save the sale first')
            self.update_possible_entry('Expense', EXPENSE_ACCOUNT, value)
            i = self.entry('Inventory')
            # Update the value for an entry that should only exist if there is a cost or a quantity
            ### NOTE: Always save quantity before item or maybe the item might get dropped!
            # TODO: Fixme
            if value!=0 and not i:
                self.create_related_entry(account=INVENTORY_ACCOUNT, tipo='Inventory', value=-value)
            elif i:
                if value!=0 or i.quantity!=0:
                    i.update('value', -value)
                else:
                    i.delete()
                    self._item=None
                    self._cost=0
        except AttributeError: self._cost=value
    cost=property(_get_cost, _set_cost)

 ################ ################ ################  Price   ################ ################ ################
    def _get_price(self):
        try: return -self.entry('Revenue').value
        except AttributeError: return self._price
    def _set_price(self, value):
        value=(value or 0)
        try:
            self.entry('Revenue').update('value',-value)
            self.entry('Client').update('value', value + self.tax - self.discount)
        except: self._price = value
    price=property(_get_price, _set_price)

 ################ ################ ################  Charge   ################ ################ ################
    def _get_charge(self):
        try: return -self.entry(self.client.name).value
        except AttributeError:
            return self._price-l._discount+l._tax
    charge=property(_get_charge)
 ################ ################ ################  Charge_before_tax   ################ ################ ################
    def _get_charge_before_tax(self):
        return self.charge-self.tax
    charge_before_tax=property(_get_charge_before_tax)
 ################ ################ ################  Price_after discount   ################ ################ ################
    def _get_price_after_discount(self):
        return self.price-self.discount
    price_after_discount=property(_get_price_after_discount)
 ################ ################ ################  Price_after discount   ################ ################ ################
    def _get_unit_price_after_discount(self):
        p=self.price_after_discount
        if self.quantity != 0 and p !=0: return p / self.quantity
        else: return p
    unit_price_after_discount=property(_get_unit_price_after_discount)
 ################ ################ ################  Unit Charge   ################ ################ ################
    def _get_unit_charge(self):
        p=self.charge
        if self.quantity != 0 and p !=0: return p / self.quantity
        else: return p
    unit_charge=property(_get_unit_charge)
 ################ ################ ################  Unit Charge   ################ ################ ################
    def _get_unit_cost(self):
        p=self.cost
        if self.quantity != 0 and p !=0: return p / self.quantity
        else: return p
    unit_cost=property(_get_unit_cost)
 ################ ################ ################  Tax   ################ ################ ################
    def _get_tax(self):
        try:
            return - self.entry('Tax').value
        except AttributeError:
            return self._tax
    def _set_tax(self, value):
        value=(value or 0)
        try:
            client=self.entry('Client').account
            self.update_possible_entry('Tax', client.tax_group.sales_tax_account, -value)
            self.entry('Client').update('value', self.price + value - self.discount)
            self._tax=0
        except: self._tax = value
    tax = property(_get_tax, _set_tax)
 ################ ################ ################  Discount   ################ ################ ################
    def _get_discount(self):
        try:
            return self.entry('Discount').value
        except AttributeError:
            return self._discount
    def _set_discount(self, value):
        value=(value or 0)
        try:
            client=self.entry('Client').account
            self.update_possible_entry('Discount', client.tax_group.discounts_account, value)
            self.entry('Client').update('value', self.price + self.tax - value)
            self._discount=0
        except: self._discount = value
    discount = property(_get_discount, _set_discount)
    def _get_charge(self):
        try:
            return self.entry('Client').value
        except AttributeError:
            return self._price+self._tax-self._discount
    charge = property(_get_charge)
    def _get_balance(self, account):
        return Entry.objects.filter(transaction__doc_number=self.doc_number, account=self.client).aggregate(total=models.Sum('value'))['total'] or Decimal('0.00')
    balance=property(_get_balance)
    def _get_overdue(self):
        if self.client.balance==0: return False
        print "self.date = " + str(self.date)
        print "self.date+timedelta(days=self.client.contact.credit_days) = " + str(self.date+timedelta(days=self.client.contact.credit_days))
        print "datetime.now() = " + str(datetime.now())
        print "self.date+timedelta(days=self.client.contact.credit_days) > datetime.now() = " + str(self.date+timedelta(days=self.client.contact.credit_days) > datetime.now())
        return self.date+timedelta(days=self.client.contact.credit_days) < datetime.now()
    overdue=property(_get_overdue)
 ################ ################ ################  (Unit Price)   ################ ################ ################
    def _get_unit_price(self):
        if self.quantity != 0 and self.price !=0: return self.price / self.quantity
        else: return self.price
    unit_price = property(_get_unit_price)
 ################ ################ ################  (Unit Discount)   ################ ################ ################
    def _get_unit_discount(self):
        if self.quantity != 0 and self.discount !=0: return self.discount / self.quantity
        else: return self.discount
    unit_discount = property(_get_unit_discount)
 ################ ################ ################  (Unit Tax)   ################ ################ ################
    def _get_unit_tax(self):
        if self.quantity != 0 and self.tax !=0: return self.tax / self.quantity
        else: return self.tax
    unit_tax = property(_get_unit_tax)
 ################ ################ ################  Total   ################ ################ ################
    def _get_total(self):
        return Decimal(str(round(self.price-self.discount+self.tax,2)))
    total=property(_get_total)
    
 ################ ################ ################  Create Entries   ################ ################ ################
def add_sale_entries(sender, **kwargs):
#    print "Sale:add_sale_entries"
    if kwargs['created']:
        l=kwargs['instance']
        if l.tipo=='Sale':
            print "l._client = " + str(l._client)
            print "l._client.tax_group = " + str(l._client.tax_group)
            account=l._client.tax_group.revenue_account
            tipo='Revenue'
        else:
            account=l._client.tax_group.returns_account
            tipo='Return'            
        if not l._tax: l._tax=0
        if not l._price: l.price=0
        if not l._discount: l._discount=0
        if not l._cost: l._cost=0
        if not l._quantity: l._quantity=0

        l.create_related_entry(
            account = account,
            tipo = tipo,
            value=l.price * -1)
        l.create_related_entry(
            account     = l._client,
            tipo        = 'Client',
            value       = l.price-l._discount+l._tax,
            item        = l._item,
            quantity    = l._quantity,
            serial      = l._serial,
            delivered   = l._delivered)
        if l.tax!=0:
            l.create_related_entry(
                account = l._client.tax_group.sales_tax_account,
                tipo = 'Tax',
                value = -l._tax)
        if l.discount!=0:
            l.create_related_entry(
                account     = l._client.tax_group.discounts_account,
                tipo        = 'Discount',
                value       = l._discount)
        if (l._quantity!=0 or l._cost!=0) and l._delivered:
#            print "creating inventory entry"
#            print "l.item = " + str(l.item)
            l.create_related_entry(
                account     = INVENTORY_ACCOUNT,
                tipo        = 'Inventory',
                value       = -l._cost,
                item        = l._item,
                quantity    = -l._quantity,
                serial      = l._serial)
            if l._cost!=0:
                l.create_related_entry(
                    account = EXPENSE_ACCOUNT,
                    tipo = 'Expense',
                    value = l._cost)

post_save.connect(add_sale_entries, sender=Sale, dispatch_uid="jade.inventory.models:add_sale_entries")

class PurchaseManager(models.Manager):
    def get_query_set(self):
        return super(PurchaseManager, self).get_query_set().filter(tipo="Purchase")
    def next_doc_number(self):
        try:
            number=super(PurchaseManager, self).get_query_set().filter(tipo="Purchase").order_by('-pk')[0].doc_number
            number=re.split("(\d*)", number)
            if number[-1]=='':
                number[-2]=str(int(number[-2])+1)
            number="".join(number)
        except: number='1001'
        return number
class Purchase(Transaction):
    class Meta:
        proxy = True
        permissions = (
            ("view_purchase", "Can view purchases"),
        )
    objects = PurchaseManager()

    def __init__(self, *args, **kwargs):
        self.template='inventory/purchase.html'
        self._cost = kwargs.pop('cost', 0)
        self._tax = kwargs.pop('tax', 0)
        self._date = kwargs.pop('date', datetime.now())
        self._delivered = kwargs.pop('delivered', True)
        self._active = kwargs.pop('active', True)
        self._item = kwargs.pop('item', None)
        self._quantity = kwargs.pop('quantity', 0)
        self._serial = kwargs.pop('serial', None)
        self._vendor = kwargs.pop('vendor', Vendor.objects.get(name=settings.DEFAULT_VENDOR_NAME))
        super(Purchase, self).__init__(*args, **kwargs)
        self._initial_cost=self.cost
        self._initial_quantity=self.quantity
        self.tipo='Purchase'
    def _get_item(self):
        try: return self.entry('Inventory').item
        except AttributeError: return self._item
    def _set_item(self, value):
        try: return [self.entry(e).update('item',value) for e in ['Inventory','Vendor']]
        except AttributeError: self._item=value
    item = property(_get_item, _set_item)
 ################ ################ ################  Active   ################ ################ ################
    def _get_active(self):
        try: return self.entry('Vendor').active
        except AttributeError: return self._active
    def _set_active(self, value):
        self._active=value
        [e.update('active',value) for e in self.entry_set.all()]
    active = property(_get_active, _set_active)
 ################ ################ ################  Delivered   ################ ################ ################
    def _get_delivered(self):
        try: return self.entry('Vendor').delivered
        except AttributeError: return self._delivered
    def _set_delivered(self, value):
        try: return [self.entry(e).update('delivered',value) for e in ['Inventory','Vendor']]
        except AttributeError: self._delivered=value
    delivered = property(_get_delivered, _set_delivered)
 ################ ################ ################  Value   ################ ################ ################
    def _get_value(self):
        return self.cost
    value=property(_get_value)
 ################ ################ ################  Quantity   ################ ################ ################
    def _get_quantity(self):
        try: return self.entry('Inventory').quantity
        except AttributeError: return self._quantity
    def _set_quantity(self, value):
        #Careful!! we have to be delicate with the quantity_left value it may have been already used!
        #TODO: Needs to be 'protected' from negative quantities
        dif=value-self.quantity
        try:
            self.entry('Vendor').update('quantity', -value)
            i=self.entry('Inventory')
            i.quantity=value
##            i.quantity_left+=dif
            i.save()
        except AttributeError: self._quantity=value
    quantity = property(_get_quantity, _set_quantity)
 ################ ################ ################  Serial   ################ ################ ################
    def _get_serial(self):
        try: return self.entry('Inventory').serial
        except AttributeError: return self._serial
    def _set_serial(self, value):
        try: return [self.entry(e).update('serial',value) for e in ['Inventory','Vendor']]
        except AttributeError: self._serial=value
    serial = property(_get_serial, _set_serial)
 ################ ################ ################  Vendor   ################ ################ ################
    def _get_vendor(self):
        try: return self.entry('Vendor').account
        except AttributeError: return self._vendor
    def _set_vendor(self, value):
        try: self.entry('Vendor').update('account', value)
        except AttributeError: self._vendor = value
    vendor = property(_get_vendor, _set_vendor)
 ################ ################ ################  Cost   ################ ################ ################
    def _get_cost(self):
        try: return self.entry('Inventory').value
        except AttributeError: return self._cost
    def _set_cost(self, value):
        dif=value-self.cost
        try:
            self.entry('Vendor').update('value', -value+self.tax)
            i=self.entry('Inventory')
            i.value=value
#            i.cost_left+=dif
            i.save()
        except AttributeError:
            self._cost=value
    cost=property(_get_cost, _set_cost)
    def _get_tax(self):
        try:
            return - self.entry('Tax').value
        except AttributeError:
            return self._tax
    def _set_tax(self, value):
        value=(value or 0)
        print "value = " + str(value)
        try:
#        vendor=self.vendor
#        vendor=self.entry('Vendor').account
#        print "vendor = " + str(vendor)
#        print "vendor.tax_group.purchase_tax_account = " + str(vendor.tax_group.purchases_tax_account)
            self.update_possible_entry('Tax', vendor.tax_group.purchases_tax_account, value)
            self.entry('Vendor').update('value', self.cost + value)
        except:
            self._tax=value
#        except: self._tax = value
    tax = property(_get_tax, _set_tax)
 ################ ################ ################  Create Entries   ################ ################ ################
def add_purchase_entries(sender, **kwargs):
    l=kwargs['instance']
    if kwargs['created']:
        l.create_related_entry(
        account = INVENTORY_ACCOUNT,
        tipo = 'Inventory',
        value = l._cost,
        item = l._item,
        quantity=l._quantity,
        serial=l._serial,
        delivered=l._delivered,
        )
        l.create_related_entry(
        account = l._vendor,
        tipo = 'Vendor',
        value = - l._cost,
        item = l._item,
        quantity=-l._quantity,
        serial=l._serial,
        delivered=l._delivered,
        )   
        if l.tax!=0:
            l.create_related_entry(
                account = l._vendor.tax_group.purchases_tax_account,
                tipo = 'Tax',
                value = l._tax)
#    if l.cost!=l._initial_cost and l.item:
#        item = l.entry("Inventory").item
#        # remove our old data from the equation
#        qty=item.stock-l.quantity
#        if l._initial_quantity!=0: cost=item.cost*item.stock-l._initial_cost
#        else: cost=item.cost*qty        

#        #calculate new cost
#        cost = (cost+l.cost)/(qty+l.quantity)
#        # save it if its new
#        if cost!=item.cost: 
#            item.cost=cost
#            item.save()

post_save.connect(add_purchase_entries, sender=Purchase, dispatch_uid="jade.inventory.models")
#post_save.connect(update_entry_costs, sender=Purchase, dispatch_uid="jade.inventory.models:update_entry_costs_for_purchases")##################################################
# Returns##################################################
class SaleReturnManager(models.Manager):
  def get_query_set(self):
    return super(SaleReturnManager, self).get_query_set().filter(tipo="SaleReturn")
    
class SaleReturn(Sale):
    class Meta:
        proxy = True
    objects = SaleReturnManager()
    def __init__(self, *args, **kwargs):
        super(SaleReturn, self).__init__(*args, **kwargs)
        self.template='inventory/sale_return.html'
        self.tipo='SaleReturn'
    def _get_price(self):
        try: return -self.entry('Return').value
        except AttributeError: return self._price
    def _set_price(self, value):
        value=(value or 0)
        try:
            self.entry('Return').update('value',-value)
            self.entry('Client').update('value', value + self.tax - self.discount)
        except: self._price = value
    price=property(_get_price, _set_price)

post_save.connect(add_sale_entries, sender=SaleReturn, dispatch_uid="jade.inventory.models")
        
class PurchaseReturnManager(models.Manager):
  def get_query_set(self):
    return super(PurchaseReturnManager, self).get_query_set().filter(tipo="PurchaseReturn")
class PurchaseReturn(Purchase):
    class Meta:
        proxy = True
    objects = PurchaseReturnManager()
    def __init__(self, *args, **kwargs):
        super(PurchaseReturn, self).__init__(*args, **kwargs)
        self.template='inventory/purchase_return.html'
        self.tipo='PurchaseReturn'
post_save.connect(add_purchase_entries, sender=PurchaseReturn, dispatch_uid="jade.inventory.models")##################################################
# Payments##################################################
class ClientPaymentManager(models.Manager):
  def get_query_set(self):
    return super(ClientPaymentManager, self).get_query_set().filter(tipo="ClientPayment")
class VendorPaymentManager(models.Manager):
  def get_query_set(self):
    return super(VendorPaymentManager, self).get_query_set().filter(tipo="VendorPayment")

class Payment(Transaction):
    class Meta:
        proxy = True
    def __init__(self, *args, **kwargs):
        self._dest = kwargs.pop('dest', None)
        self._source = kwargs.pop('source', None)
        self._value = kwargs.pop('value', Decimal('0.00'))
        super(Payment, self).__init__(*args, **kwargs)
        self.tipo='Payment'
 ################ ################ ################  Active   ################ ################ ################
    def _get_active(self):
        try: return self.entry('Debit').active
        except AttributeError: return self._active
    def _set_active(self, value):
        self._active=value
        [e.update('active',value) for e in self.entry_set.all()]
    active = property(_get_active, _set_active)

    def _get_value(self):
        try: return self.entry('Debit').value
        except AttributeError: return self._value
    def _set_value(self, value):
        try:
            self.entry('Debit').update('value',value)
            self.entry('Credit').update('value', -value)
        except: self._value = value
    value=property(_get_value, _set_value)
 ################ ################ ################  Source   ################ ################ ################
    def _get_source(self):
        try: return self.entry('Credit').account
        except AttributeError: 
            print "getting cached source"
            return self._source
    def _set_source(self, value):
        try: self.entry('Credit').update('account', value)
        except AttributeError: 
            print "setting cached source"
            self._source = value
    source = property(_get_source, _set_source)
 ################ ################ ################  Destintation   ################ ################ ################
    def _get_dest(self):
        try: return self.entry('Debit').account
        except AttributeError: return self._dest
    def _set_dest(self, value):
        try: self.entry('Debit').update('account', value)
        except AttributeError: self._dest = value
    dest = property(_get_dest, _set_dest)

 ################ ################ ################  Create Entries   ################ ################ ################
def add_payment_entries(sender, **kwargs):
    if kwargs['created']:
        l=kwargs['instance']
        l.create_related_entry(
            account = l._dest,
            tipo = 'Debit',
            value = l._value,
        )
        l.create_related_entry(
            account = l._source,
            tipo = 'Credit',
            value = -l._value,
        )

class ClientPayment(Payment):
    class Meta:
        proxy = True
    objects = ClientPaymentManager()
    def __init__(self, *args, **kwargs):
        kwargs.update({'dest':PAYMENTS_RECEIVED_ACCOUNT})
        super(ClientPayment, self).__init__(*args, **kwargs)
        self.template='inventory/client_payment.html'
        self.tipo='ClientPayment'
post_save.connect(add_payment_entries, sender=ClientPayment, dispatch_uid="jade.inventory.models")
class ClientRefundManager(models.Manager):
  def get_query_set(self):
    return super(ClientRefundManager, self).get_query_set().filter(tipo="ClientRefund")
class ClientRefund(Payment):
    class Meta:
        proxy = True
    objects = ClientRefundManager()
    def __init__(self, *args, **kwargs):
        kwargs.update({'dest':PAYMENTS_RECEIVED_ACCOUNT})
        super(ClientRefund, self).__init__(*args, **kwargs)
        self.template='inventory/client_payment.html'
        self.tipo='ClientRefund'
post_save.connect(add_payment_entries, sender=ClientRefund, dispatch_uid="jade.inventory.models")

class VendorPayment(Payment):
    class Meta:
        proxy = True
    objects = VendorPaymentManager()
    def __init__(self, *args, **kwargs):
        kwargs.update({'source':PAYMENTS_MADE_ACCOUNT})
        super(VendorPayment, self).__init__(*args, **kwargs)
        self.template='inventory/vendor_payment.html'
        self.tipo='VendorPayment'

post_save.connect(add_payment_entries, sender=VendorPayment, dispatch_uid="jade.inventory.models")

class VendorRefundManager(models.Manager):
  def get_query_set(self):
    return super(VendorRefundManager, self).get_query_set().filter(tipo="VendorRefund")
class VendorRefund(Payment):
    class Meta:
        proxy = True
    objects = VendorRefundManager()
    def __init__(self, *args, **kwargs):
        kwargs.update({'source':PAYMENTS_MADE_ACCOUNT})
        super(VendorRefund, self).__init__(*args, **kwargs)
        self.template='inventory/vendor_payment.html'
        self.tipo='VendorRefund'
post_save.connect(add_payment_entries, sender=VendorRefund, dispatch_uid="jade.inventory.models")
##################################################
# Garantees##################################################

class GaranteeOffer(models.Model):
    months = models.IntegerField(default=0, blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'), blank=True)
    item = models.ForeignKey(Item)
    site = models.ForeignKey(Site)
    objects = CurrentSiteManager()

    def __init__(self, *args, **kwargs):
        self.template='inventory/garantee_offer.html'
        super(GaranteeOffer, self).__init__(*args, **kwargs)
    def __unicode__(self):
        return 'Garantee for %i months on %s(%s)'%(self.months, self.item, str(self.price))

#class GaranteeDetail(models.Model):
#    months = models.IntegerField(default=0, blank=True)
#    transaction = models.OneToOneField(Transaction)

class Garantee(Transaction):
    # Quantity is the number of months the Garantee will be active
    class Meta:
        proxy = True
    def __init__(self, *args, **kwargs):
        self._garanteer = kwargs.pop('garanteer', None)
        self._garanteed = kwargs.pop('garanteed', None)
        self._quantity = kwargs.pop('quantity', 0)
        self._item = kwargs.pop('item', None)
        self._quantity = kwargs.pop('quantity', 0)
        self._serial = kwargs.pop('serial', None)
        self._price = kwargs.pop('price', Decimal('0.00'))
        super(Garantee, self).__init__(*args, **kwargs)
        self.tipo='Garantee'
 ################ ################ ################  Active   ################ ################ ################
    def _get_active(self):
        try: return self.entry('Garanteed').active
        except AttributeError: return self._active
    def _set_active(self, value):
        self._active=value
        [e.update('active',value) for e in self.entry_set.all()]
    active = property(_get_active, _set_active)

################ ################ ################  (Unit Price)   ################ ################ ################
    def _get_unit_price(self):
        if self.quantity != 0 and self.price !=0: return self.price / self.quantity
        else: return self.price
    unit_price = property(_get_unit_price)
################ ################ ################  Item   ################ ################ ################
    def _get_item(self):
        try: return self.entry('Garanteed').item
        except AttributeError: return self._item
    def _set_item(self, value):
        try: return [self.entry(e).update('item',value) for e in ['Garanteed','Garanteer']]
        except AttributeError: self._item=value
    item = property(_get_item, _set_item)
 ################ ################ ################  Quantity   ################ ################ ################
    def _get_quantity(self):
        try: return self.entry('Garanteed').quantity
        except AttributeError: return self._quantity
    def _set_quantity(self, value):
        value=(value or 0)
        try:
            self.entry('Garanteed').update('quantity', value)
            self.entry('Garanteer').update('quantity', -value)

        except AttributeError: self._quantity=value
    quantity = property(_get_quantity, _set_quantity)
 ################ ################ ################  Serial  ################ ################ ################
    def _get_serial(self):
        try: return self.entry('Garanteed').serial
        except AttributeError: return self._serial
    def _set_serial(self, value):
        print "setting serial"
        try: return [self.entry(e).update('serial',value) for e in ['Garanteed','Garanteer']]
        except AttributeError: 
            print "setting cache serial!!!!!!"
            self._serial=value
    serial = property(_get_serial, _set_serial)
 ################ ################ ################  Price  ################ ################ ################
    def _get_price(self):
        try: return self.entry('Garanteed').value
        except AttributeError: return self._price
    def _set_price(self, value):
        try:
            self.entry('Garanteed').update('value', value)
            self.entry('Garanteer').update('value', -value)
        except: self._price = value
    price=property(_get_price, _set_price)
 ################ ################ ################  Expires  ################ ################ ################
    def _get_expires(self):
        return in_months(self.date, self.garanteedetails.months)
    expires=property(_get_expires)
 ################ ################ ################  Create Entries   ################ ################ ################
def add_garantee_entries(sender, **kwargs):
    if kwargs['created']:
        l=kwargs['instance']
        if not l._price: l.price=0
        if not l._quantity: l._quantity=0
        l.create_related_entry(
            account     = l._garanteer,
            tipo        = 'Garanteer',
            value       = l.price * -1,
            item        = l._item,
            quantity    = -l._quantity,
            serial      = l._serial,
            delivered   = True)
        l.create_related_entry(
            account     = l._garanteed,
            tipo        = 'Garanteed',
            value       = l.price,
            item        = l._item,
            quantity    = l._quantity,
            serial      = l._serial,
            delivered   = True)

class ClientGaranteeManager(models.Manager):
  def get_query_set(self):
    return super(ClientGaranteeManager, self).get_query_set().filter(tipo="ClientGarantee")
    
class ClientGarantee(Garantee):
    class Meta:
        proxy = True
    objects=ClientGaranteeManager()
    def __init__(self, *args, **kwargs):
        self.template='inventory/client_garantee.html'
        self._client = kwargs.pop('client', None)
        kwargs['garanteed']=self.client
        if self.client: kwargs['garanteer']=self.client.tax_group.revenue_account
        super(ClientGarantee, self).__init__(*args, **kwargs)
        self.tipo='ClientGarantee'
 ################ ################ ################  Client  ################ ################ ################
    def _get_client(self):
        try: return self.entry('Garanteed').account
        except AttributeError: return self._client
    def _set_client(self, value):
        print "set_client --> value=" + str(value)
        try: self.entry('Garanteed').update('account', value)
        except AttributeError: self._client = value
    client = property(_get_client, _set_client)

post_save.connect(add_garantee_entries, sender=ClientGarantee, dispatch_uid="jade.inventory.models")

class VendorGaranteeManager(models.Manager):
  def get_query_set(self):
    return super(VendorGaranteeManager, self).get_query_set().filter(tipo="VendorGarantee")
    
class VendorGarantee(Garantee):
    class Meta:
        proxy = True
    objects=VendorGaranteeManager()
    def __init__(self, *args, **kwargs):
        self.template='inventory/vendor_garantee.html'
        self._vendor=kwargs.pop('vendor', None)
        kwargs.update({
            'garanteer': self._vendor,
            'garanteed': EXPENSE_ACCOUNT,
        })
        super(VendorGarantee, self).__init__(*args, **kwargs)
        self.tipo='VendorGarantee'
 ################ ################ ################  Vendor   ################ ################ ################
    def _get_vendor(self):
        try: return self.entry('Garanteer').account
        except AttributeError: return self._vendor
    def _set_vendor(self, value):
        try: self.entry('Garanteer').update('account', value)
        except AttributeError: self._vendor = value
    vendor = property(_get_vendor, _set_vendor)
    
post_save.connect(add_garantee_entries, sender=VendorGarantee, dispatch_uid="jade.inventory.models")


class CountDetail(models.Model):
    count = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    unit_cost = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    transaction = models.OneToOneField(Transaction)


class CountManager(models.Manager):
    def get_query_set(self):
        return super(CountManager, self).get_query_set().filter(tipo="Count")
    def next_doc_number(self):
        try:
            number=super(CountManager, self).get_query_set().filter(tipo="Count").order_by('-pk')[0].doc_number
            number=re.split("(\d*)", number)
            if number[-1]=='':
                number[-2]=str(int(number[-2])+1)
            number="".join(number)
        except: number='1001'
        return number
class Count(Transaction):
    class Meta:
        proxy = True
        permissions = (
            ("view_count", "Can view counts"),
            ("post_count", "Can post counts"),
        )
    def print_url(self):
        return '/inventory/count/%s/sheet.pdf'% self.doc_number
    objects = CountManager()
    def __init__(self, *args, **kwargs):
        self.template='inventory/count.html'
#        print "kwargs=" + str(kwargs)
        self._cost = kwargs.pop('cost', 0)
        self._unit_cost = kwargs.pop('unit_cost', 0)
        self._date = kwargs.pop('date', datetime.now())
        self._delivered = kwargs.pop('delivered', True)
        self._active = kwargs.pop('active', True)
        self._item = kwargs.pop('item', None)
#        print "self._item=" + str(self._item)
        self._quantity = kwargs.pop('quantity', 0)
        self._count = kwargs.pop('count', None)
        self._serial = kwargs.pop('serial', None)
        super(Count, self).__init__(*args, **kwargs)
        self.tipo='Count'
    def __unicode__(self):
        msg='Count'
        if str(self.doc_number)!='': msg+=" #"+self.doc_number
        try:
            if self.item: msg +=' of ' + self.item.name
        except:
            pass
        return msg
 ################ ################ ################  Value   ################ ################ ################
    def _get_value(self):
        return self.cost
    def _set_value(self, value):
        self.cost=value
    value=property(_get_value, _set_value)
 ################ ################ ################  Active   ################ ################ ################
    def _get_active(self):
        try: return self.entry('Inventory').active
        except AttributeError: return self._active
    def _set_active(self, value):
        self._active=value
        [e.update('active',value) for e in self.entry_set.all()]
    active = property(_get_active, _set_active)
 ################ ################ ################  Delivered   ################ ################ ################
    def _get_delivered(self):
        try: return self.entry('Inventory').delivered
        except AttributeError: return self._delivered
    def _set_delivered(self, value):
        try: return [self.entry(e).update('delivered',value) for e in ['Inventory','Expense']]
        except AttributeError: self._delivered=value
    delivered = property(_get_delivered, _set_delivered)
 ################ ################ ################  Item   ################ ################ ################
    def _get_item(self):
        try: return self.entry('Inventory').item
        except AttributeError: return self._item
    def _set_item(self, value):
        try: return [self.entry(e).update('item',value) for e in ['Inventory','Expense']]
        except AttributeError: self._item=value
    item = property(_get_item, _set_item)
 ################ ################ ################  Quantity   ################ ################ ################
    def _get_quantity(self):
        try: return self.entry('Inventory').quantity
        except AttributeError: return self._quantity
    def _set_quantity(self, value):
        #Careful!! we have to be delicate with the quantity_left value it may have been already used!

        dif=value-self.quantity
        try:
            self.entry('Expense').update('quantity', -value)
            i=self.entry('Inventory')
            i.quantity=value
#            if i.quantity_left+dif > 0: i.quantity_left+=dif
#            else: i.quantity_left=0
            i.save()
            # Update total cost
            try: self.cost = self.countdetail.unit_cost*value
            except ObjectDoesNotExist: self.cost = self._unit_cost*value
        except AttributeError: self._quantity=value
    quantity = property(_get_quantity, _set_quantity)
 ################ ################ ################  Serial   ################ ################ ################
    def _get_serial(self):
        try: return self.entry('Inventory').serial
        except AttributeError: return self._serial
    def _set_serial(self, value):
        try: return [self.entry(e).update('serial',value) for e in ['Inventory','Expense']]
        except AttributeError: self._serial=value
    serial = property(_get_serial, _set_serial)
 ################ ################ ################  Cost   ################ ################ ################
    def _get_cost(self):
        try: return self.entry('Inventory').value
        except AttributeError: return self._cost
    def _set_cost(self, value):
        #Careful!! we have to be delicate with the cost_left value it may have been already used!
        #TODO: What if they give us a negative cost?
#        dif=value-self.cost
        try:
            self.entry('Expense').update('value', -value)
            i=self.entry('Inventory')
            i.value=value
#            if i.cost_left+dif>0: i.cost_left+=dif
#            else: i.cost_left=0
            i.save()
        except AttributeError:
            self._cost=value
    cost=property(_get_cost, _set_cost)

    def _get_unit_cost(self):
        try: return self.countdetail.unit_cost
        except ObjectDoesNotExist: return self._unit_cost
    def _set_unit_cost(self, value):
        try:
            self.countdetail.unit_cost = value
            if self.quantity: self.cost=value*self.quantity
        except: self._unit_cost = value
    unit_cost = property(_get_unit_cost, _set_unit_cost)

    def _get_count(self):
        try: 
            return self.countdetail.count
        except ObjectDoesNotExist: 
            print "returning cached count!!!!!!"
            return self._count
    def _set_count(self, value):
        print "setting count: value=" + str(value)
        try:
            self.countdetail.count=value
            self.countdetail.save()
        except ObjectDoesNotExist: 
            print "setting cached count!!!!!"
            self._count = value
    count=property(_get_count, _set_count)

    def _get_posted(self):
        try:
            i=self.entry('Inventory')
            if i.delivered and i.active: return True
            else: return False
        except: return (self._delivered and self._active)
    def _set_posted(self, value):
        try:
            i=self.entry('Inventory')
            e=self.entry('Expense')
            i.delivered=i.active = e.delivered=e.active=value
            i.save()
            e.save()
        except: self._delivered = self._active = value
    posted=property(_get_posted, _set_posted)

    def post(self):
        if not self.item: 
            self.errors={'Item':[u'cannot be empty.',]}
            return False
        # NOTE: This could be done faster in SQL
        self.quantity = self.count - Item.objects.get(pk=self.item.pk).stock + self.quantity
        self.value = self.unit_cost * self.quantity
        self.save()
        self.errors={}
        return True
def add_count_details(sender, **kwargs):
    if kwargs['created']:
        l=kwargs['instance']
        CountDetail.objects.create(transaction=l, count=l._count, unit_cost=l._unit_cost)
post_save.connect(add_count_details, sender=Count, dispatch_uid="jade.inventory.models")
def add_count_entry(sender, **kwargs):
    if kwargs['created']:
        print "creating entries"
        l=kwargs['instance']
        if l._quantity > 0 :
            # if the value is greater than 0 then be sure to include cost_left
            print "here"
            l.create_related_entry(
                account = INVENTORY_ACCOUNT,
                tipo = 'Inventory',
                value = l.cost,
                count = l._count,
                item = l._item,
                quantity = l._quantity,
                serial = l._serial,
                delivered = l._delivered,
                cost_left = l._cost,
#                quantity_left = l._quantity,
            )
        else:
            l.create_related_entry(
                account = INVENTORY_ACCOUNT,
                tipo = 'Inventory',
                value = l.cost,
                count = l._count,
                item = l._item,
                quantity=l._quantity,
                serial=l._serial,
                delivered=l._delivered
            )
        # Always make the cooresponding Expense entry
        l.create_related_entry(
            account = EXPENSE_ACCOUNT,
            tipo = 'Expense',
            value = -l.cost,
            count = l._count,
            item = l._item,
            quantity=-l._quantity,
            serial=l._serial,
            delivered=l._delivered,
        )
post_save.connect(add_count_entry, sender=Count, dispatch_uid="jade.inventory.moddels")

class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    price_group = models.ForeignKey(PriceGroup)
    def _get_tabs(self):
        try: t=self._tabs
        except:
            self._tabs=[]
            for tab in settings.BASE_TABS:
                if self.user.has_perms(tab.permission):
                    self._tabs.append(tab)
        return self._tabs
    tabs=property(_get_tabs)
    def _get_actions(self):
        try: t=self._actions
        except:
            self._actions=[]
            for action in settings.ACTIONS:
                if self.user.has_perms(action.permission):
                    self._actions.append(action)
        return self._actions
    actions=property(_get_actions)
def add_user_profile(sender, **kwargs):
    if kwargs['created']:
        l=kwargs['instance']
        try: 
            pg=PriceGroup.objects.get(name=settings.DEFAULT_PRICE_GROUP_NAME)
            UserProfile.objects.create(user=l, price_group=pg)
        except:pass
post_save.connect(add_user_profile, sender=User, dispatch_uid="jade.inventory.moddels")
class BranchDetail(models.Model):
    account = models.OneToOneField(Account)
    db_name = models.CharField(max_length=32)
    foreign_account_name = models.CharField(_('name'), max_length=200)
    immediate = models.BooleanField(_('transfers are immediate'), default=True)
    def __unicode__(self):
        return self.account.name
    def _get_foreign_account(self):
        return Branch.objects.using(self.db_name).get(name=self.foreign_account_name)
    foreign_account=property(_get_foreign_account)

class TransferDetail(models.Model):
    remote_id = models.IntegerField()
    db_name = models.CharField(max_length=32)
    transaction = models.OneToOneField(Transaction)
    def _get_remote(self):
        try: return Transfer.objects.using(self.db_name).get(pk=self.remote_id)
        except: return None
    remote=property(_get_remote)

class TransferManager(models.Manager):
    def get_query_set(self):
        return super(TransferManager, self).get_query_set().filter(tipo="Transfer")
    def next_doc_number(self):
        try:
            number=super(TransferManager, self).get_query_set().filter(tipo="Transfer").order_by('-pk')[0].doc_number
            number=re.split("(\d*)", number)
            if number[-1]=='':
                number[-2]=str(int(number[-2])+1)
            number="".join(number)
        except: number='1001'
        return number
class Transfer(Transaction):
    class Meta:
        proxy = True
    objects = TransferManager()
    def __init__(self, *args, **kwargs):
        self.template='inventory/transfer.html'
        self._cost = kwargs.pop('cost', 0)
        self._unit_cost = kwargs.pop('unit_cost', 0)
        self._date = kwargs.pop('date', datetime.now())
        self._delivered = kwargs.pop('delivered', True)
        self._active = kwargs.pop('active', True)
        self._branch = kwargs.pop('branch',None)
        self._item = kwargs.pop('item', None)
        self._quantity = kwargs.pop('quantity', 0)
        self._serial = kwargs.pop('serial', None)
        super(Transfer, self).__init__(*args, **kwargs)
        self.tipo='Transfer'
    def __unicode__(self):
        msg='Transfer'
        if str(self.doc_number)!='': msg+=" #"+self.doc_number
        return msg
    def update_remote_entry(self, attr, value, tipo=None):
        entries=Entry.objects.using(self.detail.db_name).filter(transaction=self.detail.remote)
        if tipo: entries=entries.filter(tipo=tipo)
        for entry in entries:
            setattr(entry, attr, value)
            entry.save()
    def _get_detail(self):
        try: return self.transferdetail
        except: return None
    def _set_detail(self, value):
        self.transferdetail=value
    detail=property(_get_detail, _set_detail)
 ################ ################ ################  Value   ################ ################ ################
    def _get_value(self):
        return self.cost
    def _set_value(self, value):
        self.cost=value
    value=property(_get_value, _set_value)
 ################ ################ ################  Active   ################ ################ ################
    def _get_active(self):
        try: return self.entry('Inventory').active
        except AttributeError: return self._active
    def _set_active(self, value):
        self._active=value
        [e.update('active',value) for e in self.entry_set.all()]
        try: 
            if self.branch.branchdetail.immediate: self.update_remote_entry('active', value)
        except:pass
            
    active = property(_get_active, _set_active)
 ################ ################ ################  Delivered   ################ ################ ################
    def _get_delivered(self):
        try: return self.entry('Inventory').delivered
        except AttributeError: return self._delivered
    def _set_delivered(self, value):
        try: 
            x= [self.entry(e).update('delivered',value) for e in ['Inventory','Branch']]
            if self.branch.branchdetail.immediate: self.update_remote_entry('delivered', value)
        except AttributeError: self._delivered=value
        
    delivered = property(_get_delivered, _set_delivered)
 ################ ################ ################  Item   ################ ################ ################
    def _get_item(self):
        try: return self.entry('Inventory').item
        except AttributeError: return self._item
    def _set_item(self, value):
        try: 
            x= [self.entry(e).update('item',value) for e in ['Inventory','Branch']]
            try: self.update_remote_entry('item', value)
            except:pass
        except AttributeError: self._item=value
        
    item = property(_get_item, _set_item)
 ################ ################ ################  Quantity   ################ ################ ################
    def _get_quantity(self):
        try: return self.entry('Inventory').quantity
        except AttributeError: return self._quantity
    def _set_quantity(self, value):
        dif=value-self.quantity
        try:
            self.entry('Branch').update('quantity', value)
            self.entry('Inventory').update('quantity', -value)
            try:
                self.update_remote_entry('quantity', -value, 'Branch')
                self.update_remote_entry('quantity', value, 'Inventory')
            except:pass
        except AttributeError: self._quantity=value
    quantity = property(_get_quantity, _set_quantity)
 ################ ################ ################  Serial   ################ ################ ################
    def _get_serial(self):
        try: return self.entry('Inventory').serial
        except AttributeError: return self._serial
    def _set_serial(self, value):
        try: 
            x= [self.entry(e).update('serial',value) for e in ['Inventory','Branch']]
            try:self.update_remote_entry('serial', value)
            except:pass
        except AttributeError: self._serial=value
    serial = property(_get_serial, _set_serial)
    ################ ################ ################  branch   ################ ################ ################
    def _get_branch(self):
        try: return self.entry('Branch').account
        except AttributeError: return self._branchv
    def _set_branch(self, value):
        try: 
            if value!=self.entry('Branch').value:
                self.entry('Branch').update('account', value)
                self.delete_remote_transaction()
#                try:
#                    #Delete all entries on the other side
#                    for entry in Entry.objects.using(self.transferdetail.db_name).filter(transaction=self.transferdetail.remote): entry.delete()
#                    # Delete the transfer on the remote side
#                    self.transferdetail.remote.delete()
#                    # Also zap the transferdetail, since this will be recreated
#                    self.transferdetail.delete()
#                except:pass
                # Now rebuild using the new current branch
                self.create_remote_copy()
        except AttributeError: self._branch = value
    branch = property(_get_branch, _set_branch)
 ################ ################ ################  Cost   ################ ################ ################
    def _get_cost(self):
        try: return self.entry('Inventory').value
        except AttributeError: return self._cost
    def _set_cost(self, value):
        try:
            self.entry('Branch').update('value', value)
            i=self.entry('Inventory').update('value', -value)
            try:
                self.update_remote_entry('value', -value, 'Branch')
                self.update_remote_entry('value', value, 'Inventory')
            except:pass
        except AttributeError:
            self._cost=value
    cost=property(_get_cost, _set_cost)
    def _get_unit_cost(self):
        p=self.cost
        if self.quantity != 0 and p !=0: return p / self.quantity
        else: return p
    unit_cost=property(_get_unit_cost)
    def delete_remote_transaction(self):
        if self.detail:
            if self.detail.remote:
                for entry in Entry.objects.using(self.detail.db_name).filter(transaction=self.detail.remote): entry.delete()
                # Delete the transfer on the remote side
                self.detail.remote.delete()
            self.detail.delete()
    def create_remote_copy(self):
        remote_db=self.branch.branchdetail.db_name
        remote_account=self.branch.branchdetail.foreign_account
        foreign=RemoteTransfer()
        foreign.save(using=self.branch.branchdetail.db_name)
        # Make sure the item exists in the remote branchs db
        remote_item=Item.objects.using(remote_db).get(name=self._item.name, bar_code=self._item.bar_code)
        # Create the entries
        Entry.objects.using(remote_db).create(
            account = remote_account,
            transaction = foreign,
            tipo = 'Branch',
            value = self.cost,
            item = remote_item,
            quantity = self._quantity,
            serial = self._serial,
            delivered = self._delivered,
        )
        Entry.objects.using(remote_db).create(
            account = Account.objects.using(remote_db).get(name=settings.INVENTORY_ACCOUNT_NAME),
            transaction = foreign,
            tipo = 'Inventory',
            value = -self.cost,
            item = remote_item,
            quantity = -self._quantity,
            serial = self._serial,
            delivered = self._delivered,
        )
        self.detail=TransferDetail.objects.create(transaction=self, remote_id=foreign.pk, db_name=remote_db)
        remote=self.detail.remote
        TransferDetail(transaction=remote, remote_id=self.pk, db_name=remote.branch.branchdetail.db_name)
def delete_remote_transfer(sender, **kwargs):
    kwargs['instance'].delete_remote_transaction()
pre_delete.connect(delete_remote_transfer, sender=Transfer, dispatch_uid="jade.inventory.models")
class RemoteTransfer(Transfer):
    class Meta:
        proxy = True
    def update_remote(self, attr, value):
        # To avoid repeating myself
        pass
class RemoteItem(Item):
    class Meta:
        proxy = True

def add_transfer_entry(sender, **kwargs):
    if kwargs['created']:
        l=kwargs['instance']
        l.create_related_entry(
            account = INVENTORY_ACCOUNT,
            tipo = 'Inventory',
            value = -l.cost,
            item = l._item,
            quantity = -l._quantity,
            serial = l._serial,
            delivered = l._delivered,
        )
        l.create_related_entry(
            account = l._branch,
            tipo = 'Branch',
            value = l.cost,
            item = l._item,
            quantity=l._quantity,
            serial=l._serial,
            delivered=l._delivered,
        )
        l.create_remote_copy()
    
post_save.connect(add_transfer_entry, sender=Transfer, dispatch_uid="jade.inventory.moddels")
