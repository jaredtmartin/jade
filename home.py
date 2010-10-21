from settings import *

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'jade'             # Or path to database file if using sqlite3.
DATABASE_USER = 'root'             # Not used with sqlite3.
DATABASE_PASSWORD = 't1bur0n'         # Not used with sqlite3.

SITE_ID = 1
TEMPLATE_DIRS = ('/srv/jade/templates')
MEDIA_URL = '/chalchuapa/media'
