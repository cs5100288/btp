import  wperf.views
tornado_urlpatterns=[
    (r'/wperf/pcap_progress/(.*)', wperf.views.PcapProgressHandler),
    (r'/wperf/traceroute/(.*)', wperf.views.TracerouteHandler),
    (r'/wperf/pcap/analyze_improved/(.*)', wperf.views.PcapAnalyzeHandler),
    ]
