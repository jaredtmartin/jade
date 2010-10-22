
from settings import *

SITE_ID = 1
LOGIN_REDIRECT_URL="/chalchuapa/inventory/sales"
LOGIN_URL="/login/"
TEMPLATE_DIRS = ('/srv/jade/templates',)
MEDIA_URL = '/media'
#APP_LOCATION='/srv/jade'
#SITE_PREFIX='chalchuapa'
DEBUG = True
APP_PREFIX='/chalchuapa'
BASE_TABS = [
    Tab(label='Items', url=APP_PREFIX+'/inventory/items', permission='inventory.view_item'),
    Tab(label='Transactions', url=APP_PREFIX+'/inventory/transactions', permission='inventory.view_transaction'),
    
    Tab(label='Accounts', url=APP_PREFIX+'/inventory/accounts', permission='inventory.view_account'),
#    Tab(label='Clients', url=APP_PREFIX+'/inventory/clients', permission='inventory.view_client'),
#    Tab(label='Vendors', url=APP_PREFIX+'/inventory/vendors', permission='inventory.view_vendor'),
    Tab(label='Production', url=APP_PREFIX+'/production/production/list/', permission='production.view_production'),
]
ACTIONS = [
    Tab(label='Sales', url=APP_PREFIX+'/inventory/sales', permission='inventory.view_sale'),
    Tab(label='Purchases', url=APP_PREFIX+'/inventory/purchases', permission='inventory.view_purchase'),
    Tab(label='Counts', url=APP_PREFIX+'/inventory/counts', permission='inventory.view_count'),
    Tab(label='Transfers', url=APP_PREFIX+'/inventory/sales', permission='inventory.view_transfers'),
]
