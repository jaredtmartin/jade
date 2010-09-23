from django.conf import settings
from django.db import models
from django.db.models.fields import FieldDoesNotExist
from django.db.models import Q
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

class AccountManager(models.Manager):
    "Shows all accounts unless they are simple accounts that are not in the current site."
#    def get_query_set(self):
#        return super(AccountManager, self).get_query_set().filter(Q(site__id__exact=settings.SITE_ID)|Q(tipo__in=('Client','Branch','Vendor')))
        
#    def all(self):
#        return self.get_query_set().filter(Q(site__id__exact=settings.SITE_ID)|Q(tipo__in=('Client','Branch','Vendor')))

    def count(self):
        return self.get_query_set().filter(Q(site__id__exact=settings.SITE_ID)|Q(tipo__in=('Client','Branch','Vendor'))).count()
        
    def filter(self, *args, **kwargs):
        return self.get_query_set().filter(Q(site__id__exact=settings.SITE_ID)|Q(tipo__in=('Client','Branch','Vendor'))).filter(*args, **kwargs)

    def aggregate(self, *args, **kwargs):
        return self.get_query_set().filter(Q(site__id__exact=settings.SITE_ID)|Q(tipo__in=('Client','Branch','Vendor'))).aggregate(*args, **kwargs)

