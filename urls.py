from django.conf.urls.defaults import *
from settings import DEBUG, MEDIA_URL, MEDIA_ROOT
from django.contrib import admin
from django.views.generic.simple import direct_to_template

admin.autodiscover()

from django.contrib import databrowse
from jade.inventory.models import *

databrowse.site.register(Sale)
databrowse.site.register(Purchase)
databrowse.site.register(Count)
databrowse.site.register(Item)
databrowse.site.register(Account)
databrowse.site.register(Client)
databrowse.site.register(Vendor)



urlpatterns = patterns('',
    # Example:
    # (r'^jade/', include('jade.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^$', 'jade.inventory.views.root'),
    (r'^databrowse/(.*)', databrowse.site.root),

    (r'^admin/', include(admin.site.urls)), 
    (r'^inventory/', include('jade.inventory.urls')), 
    (r'^manual/', include('jade.manual.urls')), 
    (r'^production/', include('jade.production.urls')), 
    (r'^blocked/$',direct_to_template, {'template': 'blocked.html'},"blocked"),
    (r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, "login"),
    (r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'logout.html'}, "logout"),
#    (r'^i18n/', include('django.conf.urls.i18n')),

)

if DEBUG:
    from django.views.static import serve
    _media_url = MEDIA_URL
    if _media_url.startswith('/'):
        _media_url = _media_url[1:]
        urlpatterns += patterns('',
            (r'^%s(?P<path>.*)$' % _media_url,
            serve,
            {'document_root': MEDIA_ROOT}))
    del(_media_url, serve)
