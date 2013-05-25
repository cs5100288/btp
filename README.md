BTP Documentation
=================


## Introduction
The whole server side is a web-application. That means every analysis, every observation is available on some url. As of today(20th May, 2013), a working version exists on [agni.iitd.ac.in:8000][agni_8000]. The webserver used to be on [django][django] but its development server doesn't accept multiple connections. Some analysis took a lot of time so opening the webpage of that analysis meant that you can't open any other webpage on the server. So now the [django][django] server is wrapped inside [tornado][tornado] server. The [runserver.py][runserver.py] script allows you to run tornado server(by default) and also the django server(`python runserver.py dev`). We'll discuss the hack for running long running analysis with tornado later. First we'll describe how to make an addition/modification to any part of the project without going in depth of the individual frameworks. 

The client side is an android application. Most of the experiments and data-collections is done through it. 


## Client Side

On the client side, the main focus is to collect data that will be analyzed later. All the data was collected on a Samsung Galaxy S3. The following methods were used by us:

### Packet Trace of a single website

1. Start tcpdump. An app in the play store named [shark][shark_play_store] can do this for you.
2. Open A browser. This can be any browser. 
3. Clear all cache.
    - On the stock browser, This can be found in privacy settings
    - On firefox, this is tricky. open [about:config](about:config) and search for keyword "cache". The names are pretty self-explanatory. Adjust them e.g. minimize the premissible cache size, minimize timeout etc. This needs to be done just once. After that everytime you want the cache cleared, look in the privacy settings.
4. Open a website
5. Stop tcpdump
6. Extract the pcap file for further analysis. 

### A complex experiment involving multiple websites and/or taking ratings from users
This kind of experiments were done with [an android app][btp_app]. Earlier we used [shark][shark_play_store] to collect tcpdump but later we coded a [service][TcpdumpService.java] which does this. It needs a tcpdump binary in system path. The one we used is available [here][tcpdump_binary] It starts tcpdump at the start of experiment and ends after the last experiment. Every experiment starts with getting an experiment id from the server running at [agni][agni_8000]. After recieving the last rating, it compiles all the data collected and sends it to [agni][agni_8000] where it's saved in a database. 

In experiments involving opening multiple websites, the pcap file is a bit convoluted and determining when a particular website was first requested can be hard. So for this purpose, we need a deterministic way to distinguish the separation between the websites. The trick we used was to send a request to a pre-determined url in between the requests to different websites. We setup one such url on agni [/wperf/idle_url][/wperf/idle_url]. We use [/wperf/idle_url?sleep_time=5][/wperf/idle_url?sleep_time=5] for our purposes. 


## Django
The extensive documentation would be on the [django homepage][django]. The parts that are used will be discussed here. The folder [website][website_folder] is a `django project` with two `app`s under it. The `wperf` app has the Web performance code. 

### Requests

In a django server, when there's a request for a url, the url is matched against regular expressions in the [top level urls.py][top_level_urls.py] to find an appropriate handler. In our case, no url is mapped to a handler, instead there are two rules saying that if the url starts with "wperf/", then include [wperf/urls.py][wperf_urls.py] and search for the remaining part of the url there. Basically, if the request comes to `/wperf/pcap/list` then it will be delegated to the function [`pcap_list`][pcap_list_function] in [wperf/views.py][wperf_views.py]. 

### Responses
In a django request handler, you can return response in the following ways:

1. `return HttpResponse("plain text")`
2. `return render_to_response('template_name.html', {"key1": "value1", "key2": [1, 2, "hi"]})`. Here the `template_name.html` file should be found in the directories specified as [TEMPLATE_DIRS][template_dirs] inside [settings.py][settings.py]. The template can make use of the second argument(the dictionary) as `{{key1}} and {% for x in key2 %}{{x}} and {% endfor %}done` which would translate to `value1 and 1 and 2 and hi and done`. More on templates [here][django_templates]. 

### Database access
For databases, you define models in [models.py][wperf_models.py] and after any change, run `python manage.py syncdb` to sync up the changes. Inside the request handlers, these can be used as objects. e.g.

```python
org, org_created = models.Organization.objects.get_or_create(name=org_name, ip_range=ip_range, lower=lower_int, higher=higher_int)
h = models.Host.objects.create(org=org, stream_type=None, name="www.google.com")
h.save()

h = models.Host.objects.get(name="www.google.com")
```


## Tornado
Tornado was added as a wrapper around django-server. The request is first matched against tornado's own mapping of regex-to-handler. If found, it is served otherwise it [falls back][fall_back_on_django] on django to serve it. Tornado's url mappings are defined like [this][tornado_mappings.py]. The handlers are like this:

```python
class PcapAnalyzeHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, pcap_name):
        self.pcap_name = pcap_name
        print "Started", pcap_name
        run_background(self.analyze, self.on_complete, ())

    def analyze(self):
        print "analyzing", self.pcap_name
        try:
            self.result = pcap_analyze(None, self.pcap_name).content
        except Exception as e:
            self.result = repr(e)
        return self.result

    def on_complete(self, result):
        self.write(result)
        self.finish()
```
For time-consuming tasks, I've been using the following pattern:

1. Make a django handler. You can't know beforehand that the task is going to be time consuming so you'll do this anyway. 
2. define a tornado handler similar to the `PcapAnalyzeHandler`. 
3. In [tornado_mappings.py][tornado_mappings.py], define a mapping from the url to the handler in step 2. 
4. Keep the mapping in `urls.py` but define an additional mapping to the same handler(Like [analyze_old][analyze_old])

So if I access `/pcap/analyze/...`, it goes to tornado handler which is non-blocking but if I access `/pcap/analyze_old/...`, it goes to django handler which is blocking but will give same output. This is useful in debugging. If you get an error while accessing the non-blocking url, you can try accessing the blocking url which is served by django and so you'll get detailed info about the error/Exception.


## Analyzing pcap files
pcap files are collected on phone and then uploaded to [agni][agni_8000]. For different sorts of experiments, there are different urls where the pcap is to be uploaded. 

- For Single Website pcaps: [/wperf/pcap/list][/wperf/pcap/list]
- For an experiment involving opening multiple websites: [/wperf/pcap/obs_list][/wperf/pcap/obs_list]. The code can be modified with the knowledge of django provided earlier. 
- A comparison b/w ads enabled and ads disabled websites: [/wperf/pcap/ads_vs_no_ads_list][/wperf/pcap/ads_vs_no_ads_list]. To be clarified later. 

### Analysis of individual Pcaps
These pcaps are listed at [/wperf/pcap/list][/wperf/pcap/list]. For each of them, the analysis is available at [/wperf/pcap/analyze/name.pcap][/wperf/pcap/analyze/name.pcap]. Since the analysis runs for a while, the following techniques are used:

1. The tornado hack, as described earlier. So now [/wperf/pcap/analyze/name.pcap][/wperf/pcap/analyze/name.pcap] is the non-blocking analysis page and [/wperf/pcap/analyze_old/name.pcap][/wperf/pcap/analyze_old/name.pcap] is the blocking analysis page. If there's any error/Exception, then [/wperf/pcap/analyze/name.pcap][/wperf/pcap/analyze/name.pcap] will only show you one line of the error while [/wperf/pcap/analyze_old/name.pcap][/wperf/pcap/analyze_old/name.pcap] will show you enought to be able to debug the error. 
2. All or most of the intermediate output is stored in files. The first time analysis is run, these files are generated and from the next time onwards they are used as it is. For a pcap named `name.pcap`, the intermediate files are located in the same parent directory and their names are of the form `name*.txt`, `name*.csv` and `name.har`. Generally, to draw conclusions, tshark needs to be run many times on the pcap. The outputs of tshark are stored in files. 

The function which handles the request is [`pcap_analyze`][pcap_analyze]. Inside, `mydict` is the dictionary that will be passed to `render_to_response`. The code in general is easy to understand but is very long due to the amount of conclusions to be drawn. For graphs, we've used [Google Charts][Google Charts] and at some places, matplotlib. 

1. Google Charts: The technique here is to pass the data via `mydict` to the template, there make a javascript object with the help of `{% for %}` loop. After that, make a call to the required gallery function. Examples are provided in the documentation of Google Chargs
2. Google Charts fall short at some places, so we need to fall back to the good old `matlab` like graphs. `matplotlib` allows you to do that in python. When you need to plot multiple series with the same x-axis but the points of observation on the x-axis are not same, then you can't use google charts. 
Code example:

```python
    f = figure(figsize=(16,6))
    plt1 = f.add_subplot(111)
    pyplot.subplots_adjust(right=0.75)
    plt2 = plt1.twinx()
    plt1.set_xlim(0, max(bandwidth_data_x[-1], no_streams_with_time_x[-1]))
    plt1.set_ylim(0, max(bandwidth_data_y)*1.1)
    plt2.set_ylim(0, max(no_streams_with_time_y)*1.1)

    plt1.set_xlabel("Time")
    plt1.set_ylabel("Bandwidth")
    plt2.set_ylabel("No. of Streams")

    p1, = plt1.plot(bandwidth_data_x, bandwidth_data_y, label="Bandwidth")
    p2, = plt2.plot(no_streams_with_time_x, no_streams_with_time_y, label="No. Streams", color="r")

    plt1.legend([p1, p2], ["Bandwidth", "No. of Streams"])


    # plt1.axis["left"].label.set_color(p1.get_color())
    # plt2.axis["right"].label.set_color(p2.get_color())

    canvas = FigureCanvasAgg(f)
    output = StringIO()
    # x.save(output, "PNG")
    canvas.print_png(output)
    contents = output.getvalue().encode("base64")
    output.close()
    # f.close()
    mydict['bandwidth_numstreams_image_data'] = contents
```
Now, in the template the image can be shown as 

```html
<img src="data:image/png;base64,{{bandwidth_numstreams_image_data}}"/>
```
This way, we don't need to generate an image file and then reference it in the html. 


The analysis presented on [/wperf/pcap/analyze/name.pcap][/wperf/pcap/analyze/name.pcap] is the following: 

1. **Summary**: No. of different IP Streams, No. of different TCP Streams, Total waste TCP Streams, Total Data transfer, Total data wasted, Total dns requests, Mean DNS response time etc. 
2. A graph depicting a timeline of get requests with time with time on x-axis. This sometimes appears, sometimes not(with an error `Cannot set property 'width' of null`). Not very useful. We found alternate way for this. 
3. Amount of Data transferred for different IP addresses. 
4. **IP data transfer cdf**: Sorted amount of data transferred for different IP addresses in descending order and then in the graph, point `(x, y)` represents that first `x` ip addresses in the sorted list contribute to `y` fraction of the total data transfer. Basically some sort of CDF
5. **Data Transferred Per Organization**: Found Organizations for all the IP addresses in 3 and did the same except here we have a pie chart for relative comparison. 
6. **Org data transfer cdf**: Similar to 4, but on Organization level as 5. 
7. **No. of streams with time**: For this, Begin and End time of each stream is evaluated by tshark. Then treating these as events, we have all the times when streams were increased or decreased. The number of streams is evaluated at these times and drawn. 
8. Next graph shows bandwidth and number of streams with time in the same graph. It was not possible to draw on google charts so is drawn via matplotlib. 
9. Next graph, which sometimes doesn't show up with error `Data column(s) for axis #0 cannot be of type string`, is number of streams to TOI IPs with time. [See here][pcap_analyze_toi_streams].
10. **bandwidth with time**: For this, the function [makeBandwidthStats][makeBandwidthStats] is used. The files it writes are read and instantaneous bandwidth is evaluated at constant interval of 0.5 seconds. Which is later drawn.
11. **uplink bandwidth with time** and **downlink bandwidth with time**: Similar to 10, To determine uplink and downlink, we need to know what was the IP of the client machine(the phone on which the test was run). It is determined as the intersection of the sets {ip.dst, ip.src} for all streams. 
12. **no_streams_per_organization**: For every stream, there are two end points. One of the end points is the phone and the other is the server. Since we have deduced the ip of the phone, we know the other ip for the stream. For all these IPs, we obtain the Organization in the function [get_org_from_ip][get_org_from_ip]. 
13. **dns_requests_per_organization**: For all dns responses, find the organization of the IP address provided in the response. See [getDNSPackets][getDNSPackets]
14. **RTT With Time**: see [makeRttStats][makeRttStats]
15. **Statistics for different tcp streams**: In a pcap file, every stream is given a number. On the x-axis, there's stream number and on the y-axis, mean and st. dev. of RTT in that stream. Not very useful.
The following two graph show these for Upstream and Downstram.
16. Next, in tabular format, All this data for all streams. Individual streams are analyzed [here][individual_streams]
17. Next table is I guess a subset of the previous one. 
18. Next, for every url, download start time and time taken to download. Download start time is the time the GET request was issued. Download end time is the time when another GET request was issued in the same stream or the stream was closed(whichever comes first). 
19. **DNS Hosts**: For every host whose dns request was detected in the pcap, a table. More on this in Effect of ads section. 
20. We manually marked hosts as `"Ads", "CDN", "Host", "Social", "Other", "Unknown"` in the database, the above analysis can now be looked at from a new perspective. Following few tables and graphs demonstrate those results
21. And lastly, a solution to the problem faced in 2. `HAR` stands for HTTP Archive. There's a project called `PCAP2HAR` which converts `pcap` files into `har` files. There's a [local copy in the website folder][pcap2har_local]. We use this to produce a har file from a pcap file in the process of analysis. This har file has a static url. Now, to view the `har` file, we use an online viewer at [http://pcapperf.appspot.com/](http://pcapperf.appspot.com/). Example: [http://pcapperf.appspot.com/harviewer/index.html?inputUrl=http://agni.iitd.ac.in:8000/media/2013/02/26/shark_dump_room.har](http://pcapperf.appspot.com/harviewer/index.html?inputUrl=http://agni.iitd.ac.in:8000/media/2013/02/26/shark_dump_room.har). Such a url is put in an iframe on the analysis page. 

### Effect of browser concurrency
A few of the pcaps on [/wperf/pcap/list][/wperf/pcap/list] are named `ff_nocache_%d_%d.pcap`. These pcaps are taken in firefox on the phone with zero cache allocation size. The first number is max concurrent connections and the second number is max concurrent connections per server(`network.http.max-connections` and `network.http.maxconnections-per-server`). The url [/wperf/pcap/ff_analyze][/wperf/pcap/ff_analyze] directs to the function [ff_analyze][ff_analyze] which draws bandwidth cdf for all of these pcaps. 


### Effect of ads
To study the effect of ads, the idea is to block the ad hosts on the phone. After a pcap is analyzed, all the hosts encountered in the process are [saved in the database][class_host]. [/wperf/hosts/list][/wperf/hosts/list] lists all the hosts. The last column shows whether it is allowed or blocked. Clicking on it toggles. Toggling just makes modification in the database. Now, the mechanism to block a host on a linux device is to modify the hosts file(`/etc/hosts`) and remap the host to `127.0.0.1`. [/wperf/hosts/file][/wperf/hosts/file] provides the hosts file with current allowed/blocked status of the hosts. So overall we've established the mechanism to block a host is:

1. Set status to blocked at [/wperf/hosts/list][/wperf/hosts/list]
2. Update the hosts file of the phone. Take new hosts file from [/wperf/hosts/file][/wperf/hosts/file]. 

The Hosts tab in the application does just that. 

To study the effect of ads, The application on android had to be tweaked a bit. The commit prongs/btp@84de1aa0686bb0e43ee17ea396d799cdccd6f8e8 contains those tweaks. In this a pre-configured list of blocked hosts is kept in the code. 

1. First hosts file is modified to reflect the blocked hosts.
2. TOI website is opened with cleared cache and rating gathered
3. Hosts file is re-modified to reflect no blocked hosts
4. TOI website is opened with cleared cache and rating gathered. 
5. All collected data sent to server.


## Chrome Remote debugging
The procedure for setting up remote debugging is [here](https://developers.google.com/chrome-developer-tools/docs/remote-debugging). The timeline tab is the one that's used. The folder [chrome_toi][chrome_toi] contains two json files. They describe the timeline when ads are blocked and not blocked. They can be loaded in the timeline panel and inspected further. 


## Quality of Experience Analysis
[/wperf/pcap/obs_analyze_pca][/wperf/pcap/obs_analyze_pca] gives the regression analysis. The [code][obs_analyze_pca] is pretty much picked from examples in the documentation of [scikit-learn][scikit-learn]


## Pre-req:

1. python 2.7
    - [all packages](https://github.com/prongs/btp/blob/master/pipfreeze.txt)
    - To install, do `pip install -r pipfreeze.txt`. Not all of them are requirements, but these were all the installed packages in the end. 
2. tshark v 1.8, older versions break something




## Running:


```shell
python website/runserver.py
```


or to run in background

```shell
nohup python website/runserver.py &
```

look up [tornado_mappings.py][tornado_mappings.py], [wperf urls.py][wperf_urls.py] for url mappings.
Look up [`views.py`][wperf_views.py] for actual code.


[agni_8000]: http://agni.iitd.ac.in:8000
[tornado]: http://www.tornadoweb.org/
[django]: https://www.djangoproject.com/
[runserver.py]: https://github.com/prongs/btp/blob/master/website/runserver.py
[website_folder]: https://github.com/prongs/btp/tree/master/website
[top_level_urls.py]: https://github.com/prongs/btp/blob/master/website/urls.py
[wperf_urls.py]: https://github.com/prongs/btp/blob/master/website/wperf/urls.py
[wperf_views.py]: https://github.com/prongs/btp/tree/master/website/wperf/views.py
[wperf_models.py]: https://github.com/prongs/btp/tree/master/website/wperf/models.py
[pcap_list_function]: https://github.com/prongs/btp/blob/master/website/wperf/views.py#L306
[settings.py]: https://github.com/prongs/btp/tree/master/website/settings.py
[template_dirs]: https://github.com/prongs/btp/blob/master/website/settings.py#L92
[django_templates]: https://docs.djangoproject.com/en/dev/topics/templates/
[fall_back_on_django]: https://github.com/prongs/btp/blob/master/website/runserver.py#L46
[tornado_mappings.py]: https://github.com/prongs/btp/blob/master/website/tornado_mappings.py
[analyze_old]: https://github.com/prongs/btp/blob/master/website/wperf/urls.py#L16
[shark_play_store]: https://play.google.com/store/apps/details?id=lv.n3o.shark&feature=search_result#?t=W251bGwsMSwyLDEsImx2Lm4zby5zaGFyayJd
[btp_app]: https://github.com/prongs/btp/tree/master/app
[TcpdumpService.java]: https://github.com/prongs/btp/tree/master/app
[tcpdump_binary]: https://dl.dropboxusercontent.com/u/31703705/tcpdump
[/wperf/pcap/list]: http://agni.iitd.ac.in:8000/wperf/pcap/list
[/wperf/idle_url]: http://agni.iitd.ac.in:8000/wperf/idle_url?sleep_time=0
[/wperf/idle_url?sleep_time=5]: http://agni.iitd.ac.in:8000/wperf/idle_url?sleep_time=5
[/wperf/pcap/obs_list]: http://agni.iitd.ac.in:8000/wperf/pcap/obs_list
[/wperf/pcap/ads_vs_no_ads_list]: http://agni.iitd.ac.in:8000/wperf/pcap/ads_vs_no_ads_list
[/wperf/pcap/analyze/name.pcap]: http://agni.iitd.ac.in:8000/wperf/pcap/analyze/
[/wperf/pcap/analyze_old/name.pcap]: http://agni.iitd.ac.in:8000/wperf/pcap/analyze_old/
[pcap_analyze]: https://github.com/prongs/btp/blob/master/website/wperf/views.py#L638
[pcap_analyze_toi_streams]: https://github.com/prongs/btp/blob/master/website/wperf/views.py#L719
[Google Charts]: https://developers.google.com/chart/
[get_org_from_ip]: https://github.com/prongs/btp/blob/master/website/wperf/views.py#L521
[getDNSPackets]: https://github.com/prongs/btp/blob/master/website/wperf/views.py#L377
[makeBandwidthStats]: https://github.com/prongs/btp/blob/master/website/wperf/views.py#L477
[makeRttStats]: https://github.com/prongs/btp/blob/master/website/wperf/views.py#L624
[individual_streams]: https://github.com/prongs/btp/blob/master/website/wperf/views.py#L750
[pcap2har_local]: https://github.com/prongs/btp/tree/master/website/pcap2har
[/wperf/pcap/ff_analyze]: http://agni.iitd.ac.in:8000/wperf/pcap/ff_analyze
[ff_analyze]: https://github.com/prongs/btp/blob/master/website/wperf/views.py#L1076
[class_host]: https://github.com/prongs/btp/blob/master/website/wperf/models.py#L102
[/wperf/hosts/list]: http://agni.iitd.ac.in:8000/wperf/hosts/list
[/wperf/hosts/file]: http://agni.iitd.ac.in:8000/wperf/hosts/file
[chrome_toi]: https://github.com/prongs/btp/tree/master/chrome_toi/
[/wperf/pcap/obs_analyze_pca]: http://agni.iitd.ac.in:8000/wperf/pcap/obs_analyze_pca
[obs_analyze_pca]: https://github.com/prongs/btp/blob/master/website/wperf/views.py#L1814
[scikit-learn]: http://scikit-learn.org/stable/