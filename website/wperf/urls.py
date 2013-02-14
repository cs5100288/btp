from django.conf.urls.defaults import *
import handlers
urlpatterns = patterns('wperf.views',
        ('nextsite', 'nextsite'),
        (r'addobservation/id/(\d+)', 'addobservation'),
        ('test', 'test'),
        (r'pcap/list', 'pcap_list'),
        (r'pcap/upload', 'pcap_upload'),
        (r'pcap/analyze/(.*)', 'pcap_analyze'),
        (r'pcap/dnsquerylist/(.*)', 'pcap_dnsquerylist'),
        (r'hosts/timestamp', 'hosts_timestamp'),
        (r'hosts/list', 'hosts_list'),
        (r'hosts/file', 'hosts_file'),
        (r'hosts/detail/(.*)', 'hosts_detail'),
        (r'orgs/list', 'orgs_list'),
        (r'hosts/toggleBlocked/(.*)', 'hosts_toggleBlocked'),
        ('upload', 'upload'),
        ('list', 'listfiles'),
        ('getnewobsid', 'getnewobsid'),
        (r'map/traceroute/(.*)', 'map_traceroute'),
        ('', 'homepage'),
            )

tornado_urlpatterns = [
    (r'/wperf/pcap_progress/(.*)', handlers.PcapProgressHandler),
    (r'/wperf/traceroute/(.*)', handlers.TracerouteHandler),
    ]
