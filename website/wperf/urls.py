from django.conf.urls.defaults import *
import handlers
urlpatterns=patterns('wperf.views',
        ('nextsite','nextsite'),
        (r'addobservation/id/(\d+)','addobservation'),
        ('test', 'test'),
        (r'pcap/list', 'pcap_list'),
        (r'pcap/upload', 'pcap_upload'),
        (r'pcap/analyze/(.*)', 'pcap_analyze'),
        ('upload', 'upload'),
        ('list', 'listfiles'),
        ('getnewobsid', 'getnewobsid'),
        (r'map/traceroute/(.*)', 'map_traceroute'),
        ('','homepage'),
            )

tornado_urlpatterns=[
    (r'/wperf/pcap_progress/(.*)', handlers.PcapProgressHandler),
    (r'/wperf/traceroute/(.*)', handlers.TracerouteHandler),
    ]
