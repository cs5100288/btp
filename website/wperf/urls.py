from django.conf.urls.defaults import *
import handlers
urlpatterns = patterns('wperf.views',
        ('nextsite', 'nextsite'),
        (r'addobservation/id/(\d+)', 'addobservation'),
        ('test', 'test'),
        (r'pcap/list', 'pcap_list'),
        (r'pcap/upload', 'pcap_upload'),
        (r'pcap/obs_list', 'obs_pcap_list'),
        (r'pcap/obs_upload', 'obs_pcap_upload'),
        (r'pcap/obs_analyze/(.*)', 'obs_pcap_analyze'),
        (r'pcap/obs_analyze_old/(.*)', 'obs_pcap_analyze'),
        (r'pcap/analyze/(.*)', 'pcap_analyze'),
        (r'pcap/analyze_old/(.*)', 'pcap_analyze'),
        (r'pcap/dnsquerylist/(.*)', 'pcap_dnsquerylist'),
        (r'pcap/obs_analyze_pca', 'obs_analyze_pca'),
        (r'pcap/obs_analyze_pca_old', 'obs_analyze_pca'),
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
