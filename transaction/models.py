from django.db import models
from datetime import datetime
from django.contrib.sites.models import Site
from jade.common.models import SiteUniqueModel, prop, Setting
from django.contrib.sites.managers import CurrentSiteManager
from jade.accounting.models import Account, Client, Vendor
from jade.inventory.models import Item
from jade.common.models import get_field, increment_string_number, SiteUniqueModel, get_related_or_none
from decimal import Decimal

class DocumentManager(models.Manager):
    def next_number(self):
        try: return increment_string_number(self.get_query_set().all().order_by('-number')[0].number)
        except IndexError: return '1001'
class Document(models.Model):
    number = models.CharField(max_length=32, default='', blank=True)
    account = models.ForeignKey(Account, null=True, blank=True)
    date = models.DateTimeField(default=datetime.now())
    objects=DocumentManager()
    def default_account(self): return None
    def save(self, *args, **kwargs):
        if not self.number: self.number=self.__class__.objects.next_number()
        if not get_related_or_none(self, 'account', Account): self.account=self.default_account()
        super(Document, self).save(*args, **kwargs)
class Sale(Document):
    objects=DocumentManager()
    def default_account(self): return Setting.get('Default client')
    @models.permalink
    def get_absolute_url(self):
        return ('sale-detail', [str(self.id)])
    @models.permalink
    def get_delete_url(self):
        return ('sale-delete', [str(self.id)])
class Purchase(Document):
    objects=DocumentManager()
    def default_account(self): return Setting.get('Default vendor')
class Transaction(SiteUniqueModel):
    """    A simple transaction suitable for transferring money from one account to another.
    """
    document = models.ForeignKey(Document)
    date = models.DateTimeField(default=datetime.now())
    comments = models.CharField(max_length=200, blank=True, default='')
    value = models.DecimalField(max_digits=8, decimal_places=2, default=None)
    credit = models.ForeignKey(Account, related_name = 'credit')
    debit = models.ForeignKey(Account, related_name = 'debit')
    active = models.BooleanField(default=True)
    site = models.ForeignKey(Site)
    def default_value(self): return 0
    def default_debit(self): 
        try: return self.document.account
        except (Document.DoesNotExist,Account.DoesNotExist):return None
    def default_credit(self): 
        try: return self.document.account
        except (Document.DoesNotExist,Account.DoesNotExist):return None
    @property
    def description(self): return comments
    @property
    def number(self):
        if get_related_or_none(self, 'document', Document): return get_related_or_none(self, 'document', Document).number
        return None
    @property
    def account(self): return debit
    def default_document(self): return Document.objects.create(number=self._number)
    def __init__(self, *args, **kwargs):
        self._number=kwargs.pop('number',None)
        super(Transaction, self).__init__(*args, **kwargs)
    def save(self, *args, **kwargs):
        if not get_related_or_none(self, 'document', Document): self.document=self.default_document()
        if not get_related_or_none(self, 'debit', Account): self.debit=self.default_debit()
        if not get_related_or_none(self, 'credit', Account): self.credit=self.default_credit()
        if not self.value: self.value=self.default_value()
        super(Transaction, self).save(*args, **kwargs)
    @property
    def applied_value(self):
        if not self.active: return 0
        return self.value
    
# Add properties to Account and Item to get balance and stock
def get_balance(self):
    """    Allows an account to calculate its balance based on transactions made
    """
    return (Transaction.objects.filter(debit=self, active=True).aggregate(total=models.Sum('value'))['total'] or Decimal('0.00'))         -(Transaction.objects.filter(credit=self, active=True).aggregate(total=models.Sum('value'))['total'] or Decimal('0.00'))         * self.multiplier
Account.balance=property(get_balance)

class InventoryTransaction(Transaction):
    """    A Transaction that moves inventory as well as money
    """
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=None, null=True)
    item = models.ForeignKey(Item, blank=True, null=True)
    serial = models.CharField(max_length=32, null=True, blank=True)
    def default_quantity(self): return 1
    def save(self, *args, **kwargs):
        if not self.quantity: self.quantity=self.default_quantity()
        super(InventoryTransaction, self).save(*args, **kwargs)
    @property
    def description(self): 
        try: return self.item.name
        except AttributeError: return self.comments

def get_stock(self):
    """    retreives the amount of stock in inventory for an item by summing all of the quantities for the item
    """    
    return (InventoryTransaction.objects.filter(item=self, debit=Setting.get('Inventory account'), active=True).aggregate(total=models.Sum('quantity'))['total'] or Decimal('0.00'))-(InventoryTransaction.objects.filter(item=self, credit=Setting.get('Inventory account'), active=True).aggregate(total=models.Sum('quantity'))['total'] or Decimal('0.00'))
Item.stock=property(get_stock)
def get_total_cost(self):
    """    Returns the total cost of all of a certain item in stock
    """
    return (InventoryTransaction.objects.filter(item=self, debit=Setting.get('Inventory account'), active=True).aggregate(total=models.Sum('value'))['total'] or Decimal('0.00'))-(InventoryTransaction.objects.filter(item=self, credit=Setting.get('Inventory account'), active=True).aggregate(total=models.Sum('value'))['total'] or Decimal('0.00'))
Item.total_cost=property(get_total_cost)
def get_cost(self):
    """    calculates cost based on entries
    """      
    stock=self.stock
    if stock==0: return 0
    return self.total_cost/self.stock
Item.cost=property(get_cost)
def price(self, client):
    """ Calculates price for an item for a given client using fixed and relative values
    """
    price=self._price_for_client(client)
    return Decimal(str(round(self.cost*price.relative + price.fixed,2)))
Item.price=price

class Line(InventoryTransaction):
    """    A transaction that has both inventory and can be marked as delivered or not delivered
    """
    delivered = models.BooleanField(default=True)
    @property
    def applied_quantity(self):
        if not self.delivered: return 0
        return self.quantity
       
class Payment(Transaction):
    pass
class SalePayment(Payment):
    pass
class PurchasePayment(Payment):
    pass
class Refund(Transaction):
    pass
class SaleRefund(SalePayment):
    pass
class PurchaseRefund(PurchasePayment):
    pass
class Cost(InventoryTransaction):
    pass
class SaleLine(Line):
    """    A Transaction where the debit is a client and the credit is the revenue account
            Sales also create a Cost Transaction automaticly when saved if they have an item
    """
    cost_transaction = models.ForeignKey(Cost, null=True)
     
    def default_document(self): return Sale.objects.create(number=self._number)
    def default_value(self): 
        if get_related_or_none(self, 'item', Item): return self.item.price(self.debit)
        else: return 0
    def default_credit(self): return Setting.get('Revenue account')
    def save(self, *args, **kwargs):
        """    Creates cost transaction if there is an item
        """
        self.update_cost()
        super(SaleLine, self).save(*args, **kwargs)
    def update_cost(self):
        """    Creates or updates the cost associated with this sale to the current cost of the item(s) sold
        """
        try:cost=self.cost_transaction
        except Cost.DoesNotExist: cost=None
        try:value=self.item.cost*(self.quantity or 0)
        except AttributeError: value=0
        if cost: 
            cost.value=value
            cost.item=self.item
            cost.quantity=self.quantity
            cost.active=self.active
        else:
            cost=Cost(
                credit=Setting.get('Inventory account'),
                debit=Setting.get('Inventory expense account'),
                value=value,
                item=self.item,
                quantity=self.quantity,
                active=self.active,
            )
        cost.save()
        self.cost_transaction=cost

class PurchaseLine(Line):    
    @property
    def account(self): return credit
    def default_document(self): return Purchase.objects.create(number=self._number)
    def default_debit(self): return Setting.get('Inventory account')
    def default_value(self): 
        if get_related_or_none(self, 'item', Item): return self.item.cost*(self.quantity or 1)
        else: return 0        
    def save(self, *args, **kwargs):
        self.debit=Setting.get('Inventory account')
        super(PurchaseLine, self).save(*args, **kwargs)
        
class Count(InventoryTransaction):
    pass
    
class Transfer(InventoryTransaction):
    pass
