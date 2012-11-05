import  wperf.handlers
tornado_urlpatterns=[
    (r'/wperf/pcap_progress/(.*)', wperf.handlers.PcapProgressHandler),
    (r'/wperf/traceroute/(.*)', wperf.handlers.TracerouteHandler),
    ]
