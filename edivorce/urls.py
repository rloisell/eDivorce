from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = []

if settings.ENVIRONMENT in ['localdev', 'dev', 'test', 'minishift']:
    import debug_toolbar
    urlpatterns.append(url(r'^__debug__/', include(debug_toolbar.urls)),)

if settings.ENVIRONMENT in ['localdev', 'minishift']:
    urlpatterns.append(url(r'^admin/', admin.site.urls))

urlpatterns.append(url(r'^', include('edivorce.apps.core.urls')))
