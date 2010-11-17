from django.conf import settings
from django.db import models
from django.db.models.fields import FieldDoesNotExist
from django.db.models import Q
from django.contrib.sites.models import Site
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
class ClientManager(models.Manager):
    def default(self):
        return super(ClientManager, self).get_query_set().get(name=settings.DEFAULT_CLIENT_NAME)
    def next_number(self):
        number=super(ClientManager, self).get_query_set().filter(tipo="Client").order_by('-number')[0].number
        return increment_string_number(number)
    def get_or_create_by_name(self, name):
        try:
            return super(ClientManager, self).get_query_set().get(name=name)
        except:
            if name and name != '':
                if settings.AUTOCREATE_CLIENTS:
                    price_group=PriceGroup.objects.get(name=settings.DEFAULT_PRICE_GROUP_NAME)
                    tax_group=TaxGroup.objects.get(name=settings.DEFAULT_TAX_GROUP_NAME)
                    number=Client.objects.next_number()
                    return super(ClientManager, self).create(name=name,price_group=price_group,tax_group=tax_group, number=number)
            else:
                return super(ClientManager, self).get_query_set().get(name=settings.DEFAULT_CLIENT_NAME)
    def get_query_set(self):
        return super(ClientManager, self).get_query_set().filter(tipo="Client")
class VendorManager(models.Manager):
    def default(self):
        return super(VendorManager, self).get_query_set().get(name=settings.DEFAULT_VENDOR_NAME)
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
                if settings.AUTOCREATE_VENDORS:
                    price_group=PriceGroup.objects.get(name=settings.DEFAULT_PRICE_GROUP_NAME)
                    tax_group=TaxGroup.objects.get(name=settings.DEFAULT_TAX_GROUP_NAME)
                    return super(VendorManager, self).create(name=name,price_group=price_group,tax_group=tax_group)
            else:
                return super(VendorManager, self).get_query_set().get(name=settings.DEFAULT_VENDOR_NAME)
class EntryManager(models.Manager):
    def get_query_set(self):
        return super(EntryManager, self).get_query_set().filter(site=Site.objects.get_current())
class BaseManager(models.Manager):
    def __init__(self, tipo):
        super(BaseManager, self).__init__()
        self.tipo=tipo
    def get_query_set(self):
        return super(BaseManager, self).get_query_set().filter(tipo=self.tipo)
    def next_doc_number(self):
        try: 
            number = super(BaseManager, self).get_query_set().filter(tipo=self.tipo).order_by('-pk')[0].doc_number
            number=re.split("(\d*)", number)
            if number[-1]=='':
                number[-2]=("%%0%id" % len(number[-2])) % (int(number[-2])+1)
            return "".join(number)
        except: return "1001"    
class SaleManager(BaseManager):
    def next_doc_number(self):
        try: 
            number = super(BaseManager, self).get_query_set().filter(tipo=self.tipo).order_by('-pk')[0].doc_number
            number=re.split("(\d*)", number)
            if number[-1]=='':
                number[-2]=("%%0%id" % len(number[-2])) % (int(number[-2])+1)
            return "".join(number)
        except: return "1001"    

#class AccountManager(models.Manager):
#    "Shows all accounts unless they are simple accounts that are not in the current site."
##    def get_query_set(self):
##        return super(AccountManager, self).get_query_set().filter(Q(site__id__exact=settings.SITE_ID)|Q(tipo__in=('Client','Branch','Vendor')))
#        
##    def all(self):
##        return self.get_query_set().filter(Q(site__id__exact=settings.SITE_ID)|Q(tipo__in=('Client','Branch','Vendor')))

#    def count(self):
#        return self.get_query_set().filter(Q(site__id__exact=settings.SITE_ID)|Q(tipo__in=('Client','Branch','Vendor'))).count()
#        
#    def filter(self, *args, **kwargs):
#        return self.get_query_set().filter(Q(site__id__exact=settings.SITE_ID)|Q(tipo__in=('Client','Branch','Vendor'))).filter(*args, **kwargs)

#    def aggregate(self, *args, **kwargs):
#        return self.get_query_set().filter(Q(site__id__exact=settings.SITE_ID)|Q(tipo__in=('Client','Branch','Vendor'))).aggregate(*args, **kwargs)
class ItemManager(models.Manager):
    def next_bar_code(self):
        try:
            number=super(ItemManager, self).get_query_set().all().order_by('-bar_code')[0].bar_code
            number=increment_string_number(number)
            while Item.objects.filter(bar_code=number).count()>0:
                number=increment_string_number(number)
            return number
        except: return '1'
    def find(self, q):
        query=super(ItemManager, self).get_query_set()
        for key in q.split():
            query=query.filter(Q(name__icontains=key) | Q(bar_code__icontains=key)|Q(description__icontains=key))
        return query
    def fetch(self, q):
        return super(ItemManager, self).get_query_set().get(Q(name=q) | Q(bar_code=q))
    def low_stock(self):
        return list(Item.objects.raw("select id from (select inventory_item.*, sum(quantity) total from inventory_item left join inventory_entry on inventory_item.id=inventory_entry.item_id where (inventory_entry.delivered=True and account_id=%i) or (inventory_entry.id is null) group by inventory_item.id) asd where (total<minimum) or (total is null and minimum>0);" % INVENTORY_ACCOUNT.pk))

