from django.conf.urls.defaults import *
urlpatterns=patterns('wperf.views',
        ('nextsite','nextsite'),
        (r'addobservation/id/(\d)','addobservation'),
        ('test', 'test'),
        ('upload', 'upload'),
        ('list', 'listfiles'),
        ('getnewobsid', 'getnewobsid'),
        ('','homepage'),
            )

