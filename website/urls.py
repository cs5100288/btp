from django.conf.urls.defaults import *
from django.conf import settings
from django.conf.urls.static import static
import os

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    (r'^vperf/', include('Video_Performance.urls')),
    (r'^wperf/', include('wperf.urls')),
    #(r'^ctrl/', include('ctrl.urls')),
    #(r'^log/', include('log.urls')),


    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
# static files
#urlpatterns += patterns('', (r'^static/(.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),)
urlpatterns+=static(settings.STATIC_URL, document_root=os.getcwd()+"/Video_Performance/static/")

# media files
urlpatterns+=static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



