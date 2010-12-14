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
# Django settings for jade project.
from django.utils.translation import ugettext_lazy as _
import os
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'jade'             # Or path to database file if using sqlite3.
DATABASE_USER = 'root'             # Not used with sqlite3.
DATABASE_PASSWORD = 't1bur0n'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'es'
#LANGUAGES = (
#  ('de', _('German')),
#  ('en', _('English')),
#  ('es', _('Spanish')),
#  ('fr', _('French')),
#)

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
#MEDIA_ROOT = ''
MEDIA_ROOT = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'
APP_LOCATION='/home/jared/Jade/jade'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '-mfp!4i9u$)3ti5u+s5$&j*$w)$qv3(j_t3ohc(bmpu-%ic0y7'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)
LOGIN_REDIRECT_URL="/inventory/sales"
LOGIN_URL="/login/"
MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    "jade.inventory.context.company_name",
)

AUTH_PROFILE_MODULE = 'inventory.UserProfile'
ROOT_URLCONF = 'jade.urls'

TEMPLATE_DIRS = (
    '/home/jared/Jade/jade/templates'
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    )
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'jade.inventory',
    'jade.production',
    'jade.manual',
    'django.contrib.markup',
    'django_extensions',
    'django.contrib.databrowse',
    )
class Tab():
    def __init__(self, label, url, permission):
        self.label=label
        self.url=url
        self.permission=permission
BASE_TABS = [
    Tab(label='Items', url='/inventory/items/', permission='inventory.view_item'),
    Tab(label='Transactions', url='/inventory/transactions/', permission='inventory.view_transaction'),
    
    Tab(label='Accounts', url='/inventory/accounts/', permission='inventory.view_account'),
#    Tab(label='Clients', url='/inventory/clients', permission='inventory.view_client'),
#    Tab(label='Vendors', url='/inventory/vendors', permission='inventory.view_vendor'),
    Tab(label='Production', url='/production/production/list/', permission='inventory.view_production'),
]
ACTIONS = [
    Tab(label='Sales', url='/inventory/sales/', permission='inventory.view_sale'),
    Tab(label='Purchases', url='/inventory/purchases/', permission='inventory.view_purchase'),
    Tab(label='Counts', url='/inventory/counts/', permission='inventory.view_count'),
    Tab(label='Transfers', url='/inventory/sales/', permission='inventory.view_transfer'),
]
#ASSETS_ACCOUNT_DATA=('Activos','01', 1)
#CASH_ACCOUNT_DATA=('Efectivo','0101', 1)
#PAYMENTS_RECEIVED_ACCOUNT_DATA=('Efectivo','0101', 1)
#PAYMENTS_MADE_ACCOUNT_DATA=('Efectivo','0101', 1)
#INVENTORY_ACCOUNT_DATA=('Inventario','0102', 1)
#BANK_ACCOUNT_DATA=('Banco','0103', 1)
#CLIENTS_ACCOUNT_DATA=('Clientes','0103', 1)
#DEFAULT_CLIENT_DATA=('Anonimo','010301', 1)
#LIABILITIES_ACCOUNT_DATA=('Pasivos','02', -1)
#VENDORS_ACCOUNT_DATA=('Proveedores','0201', -1)
#DEFAULT_VENDOR_DATA=('No Specificado','020101', -1)
#TAX_ACCOUNT_DATA=('Impuestos','0202', -1)
#SALES_TAX_ACCOUNT_DATA=('Impuestos de Ventas','020201', -1)
#DEFAULT_SALES_TAX_ACCOUNT_DATA=('Impuestos de Ventas de Consumidor Final','02020101', -1)
#PURCHASES_TAX_ACCOUNT_DATA=('Impuestos de Compras','020202', -1)
#DEFAULT_PURCHASES_TAX_ACCOUNT_DATA=('Impuestos de Compras de Consumidor Final','02020201', -1)
#EQUITY_ACCOUNT_DATA=('Patrocinio','03', -1)
#REVENUE_ACCOUNT_DATA=('Ingresos','04', -1)
#SUB_REVENUE_ACCOUNT_DATA=('Ingresos de Consumidor Final','0401', -1)
#DEFAULT_REVENUE_ACCOUNT_DATA=('Ventas de Consumidor Final','040101', -1)
#DEFAULT_DISCOUNTS_ACCOUNT_DATA=('Descuentos de Consumidor Final','040102', -1)
#DEFAULT_RETURNS_ACCOUNT_DATA=('Devoluciones de Consumidor Final','040103', -1)
#EXPENSE_ACCOUNT_DATA=('Gastos','05', 1)
#INVENTORY_EXPENSE_ACCOUNT_DATA=('Gastos de Inventario','0501', 1)
#COUNTS_EXPENSE_ACCOUNT_DATA=('Gastos de Cuentas Fisicas','0502', 1)
#TRANSFER_ACCOUNT_DATA=('Transferencias','0503', 1)
#PRODUCTION_EXPENSE_ACCOUNT_DATA=('Gastos de Produccion','0501', 1)

#DEFAULT_CLIENT_NAME=DEFAULT_CLIENT_DATA[0]
#DEFAULT_VENDOR_NAME=DEFAULT_VENDOR_DATA[0]
#COMPANY_NAME='ACME Industrias'
#DEFAULT_FIXED_PRICE=0
#AUTOCREATE_CLIENTS=True
#AUTOCREATE_VENDORS=True
#DEFAULT_RELATIVE_PRICE=1
#DEFAULT_PRICE_GROUP_NAME='Publico'
#DEFAULT_TAX_GROUP_NAME='Consumidor Final'
#DEFAULT_TAX_INCLUDED=True
#DEFAULT_ACCOUNTING_DEBIT_ACCOUNT_NAME='Efectivo'
#DEFAULT_ACCOUNTING_CREDIT_ACCOUNT_NAME='Gastos'
#DATE_FORMAT="m/d/Y"
#RECEIPT_REPORT_NAME_SUFFIX=''
#RECEIPT_REPORT_NAME_PREFIX='Factura de '
#COUNT_SHEET_REPORT_NAME='Hoja de Cuentas Fisicas'
#LABEL_SHEET_REPORT_NAME='Hoja de Etiquetas'
#PRICE_REPORT_NAME='Hoja de Precios'
#INVENTORY_REPORT_NAME='Reporte de Inventario'
#MOVEMENTS_REPORT_NAME='Reporte de Movimientos'
#LOW_STOCK_REPORT_NAME='Reporte de Baja Inventario'
#GARANTEE_REPORT_NAME='Reporte de Garantias'
#JOB_REPORT_NAME='Reporte de Orden de Produccion'
#PROCESS_REPORT_NAME='Reporte de Proceso de Produccion'
#CASH_CLOSING_REPORT_NAME='Corte de Caja'
#ACCOUNT_STATEMENT_REPORT_NAME='Estado de Cuentas'
#QUOTE_TEMPLATE_NAME='Cotizacion'
#DEFAULT_UNIT_NAME='Cada Uno'
#DEFAULT_CREDIT_DAYS=30
#BARCODES_FOLDER='media/barcodes/'
#LABELS_PER_LINE=4
#LABELS_PER_PAGE=44
#STARTING_CASH_ACCOUNT_BALANCE=30
#DEFAULT_ACCOUNT_GROUP_NAME='Consumidor Final'
#DEFAULT_RECEIPT_GROUP_NAME='Consumidor Final'
