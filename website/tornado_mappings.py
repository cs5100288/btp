import wperf.views
import tornado.web


tornado_urlpatterns = [
    (r'/favicon.ico', tornado.web.RedirectHandler, {"url": "/static/fire.gif"}),
    (r'/wperf/pcap_progress/(.*)', wperf.views.PcapProgressHandler),
    (r'/wperf/traceroute/(.*)', wperf.views.TracerouteHandler),
    (r'/wperf/geoip/(.*)', wperf.views.GeoIpHandler),
    (r'/wperf/pcap/analyze/(.*)', wperf.views.PcapAnalyzeHandler),
    (r'/wperf/pcap/obs_analyze/(.*)', wperf.views.ObsPcapAnalyzeHandler),
    (r'/wperf/pcap/ads_vs_no_ads_analyze/(.*)', wperf.views.AdsVsNoAdsPcapAnalyzeHandler),
    (r'/wperf/pcap/obs_analyze_pca', wperf.views.PCAHandler),
    (r'/wperf/idle_url', wperf.views.IdleUrlHandler),
]
