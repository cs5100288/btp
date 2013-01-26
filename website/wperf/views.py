# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.template import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import *
from django.core.urlresolvers import reverse
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import models
import forms
import os
import sys
import commands
import subprocess
import re
import csv
import urllib
import urllib2
import random
import csv
import datetime
import socket


def whois(ip):
    p = subprocess.Popen(" ".join(["whois", ip]), stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    op = p.stdout.read()
    print p.stderr.read()
    result = {}
    for line in op.split("\n"):
        if len(line.strip()) == 0:
            continue
        if line[0] in ["#", "%"]:
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        result[k.strip()] = v.strip()
    print ip, result
    return result


def filebasename(fn):
    return os.path.splitext(os.path.basename(fn))[0]


def homepage(request):
    mydict = {}
    return render_to_response('wperf_index.html', mydict)


def nextsite(request):
    last = models.Website.objects.count() - 1
    rand_index = random.randint(0, last)
    chosenOne = models.Website.objects.all()[rand_index]
    return HttpResponse(chosenOne.address)


@csrf_exempt
def addobservation(request, pk):
    if request.method == 'POST':
        datas = request.POST['data']
        data = eval(datas)
        for key in data.keys():
            w = models.Website()
            w.testId = models.Test.objects.get(pk = int(pk))
            w.url = key
            w.pageLoadTime = data[key]['pageLoadTime']
            w.rating = data[key]['rating']
            w.progressTimeMap = data[key]['progressTimeMap']
            w.save()
        return HttpResponse("")


@csrf_exempt
def getnewobsid(request):
    if request.method == 'POST':
        w = models.Test()
        w.tester = request.POST['tester']
        w.gsmCellId = request.POST['gsmCellId']
        w.operator = request.POST['operator']
        w.networkType = request.POST['networkType']
        w.save()
        return HttpResponse("id:" + str(w.pk))


def test(request):
    mydict = {}
    return render_to_response('test.html', mydict)


def listfiles(request):
    form = forms.UploadForm()
    return render_to_response(
                'list.html',
                {'uploadedfiles': models.UploadedFile.objects.all(), 'form': form},
                context_instance=RequestContext(request)
                )


def upload(request):
    if request.method == 'POST':
        form = forms.UploadForm(request.POST, request.FILES)
        if form.is_valid():
            newfile = models.UploadedFile(filetype="None", uploadedfile=request.FILES['uploadfile'], shortfilename=request.FILES['uploadfile'].name, processed=False)
            newfile.save()
            s = newfile.uploadedfile.name
            s = s[s.rfind('/') + 1:]
            newfile.shortfilename = s
            newfile.save()
            return HttpResponseRedirect(reverse(listfiles))
    else:
        form = forms.UploadForm()
        return render_to_response(
                'list.html',
                {'uploadedfiles': [], 'form': form},
                context_instance=RequestContext(request)
                )


def pcap_list(request):
    form = forms.UploadForm()
    return render_to_response('pcap_list.html', {'pcap_files': models.PcapFile.objects.all(), 'form': form}, context_instance=RequestContext(request))


def pcap_upload(request):
    if request.method == 'POST':
        form = forms.UploadForm(request.POST, request.FILES)
        if form.is_valid():
            newpcap = models.PcapFile(uploadedfile=request.FILES['uploadfile'], shortfilename=request.FILES['uploadfile'].name)
            newpcap.save()
            s = newpcap.uploadedfile.name
            s = s[s.rfind('/') + 1:]
            newpcap.shortfilename = s
            newpcap.save()
            return HttpResponseRedirect(reverse(pcap_list))
    else:
        form = forms.UploadForm()
        return render_to_response('pcap_list.html', {'pcap_files': [], 'form': form}, context_instance=RequestContext(request))


class DNS(object):
    def __init__(self, dns_id):
        self.dns_id = dns_id
        self.queries = []
        self.queryhosts = []
        self.responses = []


def getDNSPackets(filename, dnspath=None):
    if not dnspath:
        a, b = os.path.splitext(filename)
        dnspath = a + "_dns.txt"
    if not os.path.exists(dnspath):
        print "not exits"
        cmd1 = """tshark -n -R "dns" -r %s""" % (filename)
        p = subprocess.Popen(cmd1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        with open(dnspath, 'w') as f:
            r = p.stdout.read()
            f.write(r)

    dns_list = {}
    ip_to_dns_id = {}
    with open(dnspath) as f:
        for line in f.read().split("\n"):
            if(len(line.strip()) == 0):
                continue
            m = re.match(r'\s*(\d+)\s+(.*?)\s+(\d+\.\d+\.\d+\.\d+)\s+->\s+(\d+\.\d+\.\d+\.\d+)\s+DNS\s+\d+\s+Standard\s+query\s+(response\s+)?(.*?)\s+(.*)', line.strip())
            # print m.groups()
            # return
            if m:
                packet_no, packetTime, fromIp, toIp, whetherResponse, dns_id, dns_string = m.groups()
                dns_list.setdefault(dns_id, DNS(dns_id))
                if whetherResponse:
                    dns_list[dns_id].responses.append((packetTime, fromIp, toIp, dns_string))
                    m1 = re.findall(r'A\s+(\d+\.\d+\.\d+\.\d+)', dns_string)
                    for ip in m1:
                        ip_to_dns_id.setdefault(ip, [])
                        ip_to_dns_id[ip].append(dns_id)
                else:
                    dns_list[dns_id].queries.append((packetTime, fromIp, toIp, dns_string))
                    if dns_string[:2] == "A ":
                        dns_list[dns_id].queryhosts.append(dns_string[2:].strip())
        return (dns_list, ip_to_dns_id)


def makeStats(filename, csvpath=None):
    if not csvpath:
        a, b = os.path.splitext(filename)
        csvpath = a + ".csv"
    p_ip = subprocess.Popen(cmd1_ip, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    streams = sorted(list(set(map(int, filter(lambda x: len(x) > 0, map(lambda x: x.strip(), p.stdout.read().split('\n')))))))

    with open(csvpath, "wb") as csvfile:
        writer = csv.writer(csvfile)
        for s in streams:
            cmd2 = """tshark -r %s -q -z conv, tcp, tcp.stream==%d""" % (filename, s)
            cmd3 = """tshark -n -R "tcp.stream==%d && http contains GET" -r %s -T fields -e http.request.full_uri """ % (s, filename)

            q1 = subprocess.Popen(cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            q2 = subprocess.Popen(cmd3, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

            l = q1.stdout.read().split("\n")[5]
            m = re.match(r'\s*(\d+\.\d+\.\d+\.\d+):.*?\s+<->\s+(\d+\.\d+\.\d+\.\d+):.*?\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)\s+(.*?)\s+(.*?)\s+?', l)
            ip1, ip2, transfer, startTime, duration = m.groups(0)

            objects = map(lambda x: x.strip(), q2.stdout.read().strip().split('\n'))
            num_objects = len(objects)
            url = "%d objects with url like %s..." % (num_objects, objects[0][:50])
            if len(objects[0].strip()) == 0:
                url = "No objects fetched"
            writer.writerow([ip1, ip2, transfer, startTime, duration, url])
    with open(csv2_path, 'wb') as csv2_file:
        writer = csv.writer(csv2_file)
        for line in p_ip.stdout.read().split("\n")[5:]:
            m = re.match(r'\s*(\d+\.\d+\.\d+\.\d+).*?\s+<->\s+(\d+\.\d+\.\d+\.\d+).*?\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)\s+(.*?)\s+(.*?)\s+?', line)
            if not m:
                continue
            ip1, ip2, transfer, startTime, duration = m.groups(0)
            writer.writerow([ip1, ip2, transfer, startTime, duration])


def intersect(l1, l2):
    return [x for x in l1 if x in l2] if l2 is not None else l1


def other(x, l):
    return l[1] if x == l[0] else l[0]


def pcap_analyze(request, pcap_name):
    m = models.PcapFile.objects.get(shortfilename=pcap_name)
    a, b = os.path.splitext(m.uploadedfile.path)
    c, d = os.path.splitext(pcap_name)
    csvpath = a + ".csv"
    csv2_path = a + "_ip.csv"
    if not os.path.exists(csvpath) or not os.path.exists(csv2_path):
        makeStats(m.uploadedfile.path, csvpath)
    d = {}
    dns_list, ip_to_dns_id = getDNSPackets(m.uploadedfile.path)
    with open(csvpath) as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            ip1, ip2, transfer, startTime, duration, url = row
            d.setdefault((ip1, ip2), [])
            d[(ip1, ip2)].append([transfer, startTime, duration, url])

    mydict = {}
    no_ip_streams, no_tcp_streams, total_data_transfer, total_data_waste, no_tcp_waste_streams = 0, 0, 0, 0, 0
    myip = None
    maxlen = 0
    for k in d:
        myip = intersect(k, myip)
        maxlen = max(maxlen, len(d[k]))
        total_data_transfer += sum(int(xx[0]) for xx in d[k])
        total_data_waste += sum(int(xx[0]) for xx in d[k] if xx[3].find('No objects') == 0)
        no_tcp_waste_streams += sum(1 for xx in d[k] if xx[3].find('No objects') == 0)
        no_ip_streams += 1
        no_tcp_streams += len(d[k])
    _myip = myip[0]
    d2 = []
    ips = []
    for k in d:
        l = len(d[k])
        xx = []
        o_ip = other(_myip, k)
        if ip_to_dns_id.has_key(o_ip):
            for dns_query_id in ip_to_dns_id[o_ip]:
                if dns_list[dns_query_id].queries and dns_list[dns_query_id].responses:
                    query_time = min(float(q[0]) for q in dns_list[dns_query_id].queries)
                    response_time = min(float(q[0]) for q in dns_list[dns_query_id].responses)
                    xx.append([response_time + 5, response_time, query_time, query_time - 5, 'DNS Qusadfadfery for ' + dns_list[dns_query_id].queries[0][3]])
        maxlen = max(maxlen, len(d[k]) + len(xx))

    mydict['no_ip_streams'] = no_ip_streams
    mydict['no_tcp_streams'] = no_tcp_streams
    mydict['no_tcp_waste_streams'] = no_tcp_waste_streams
    mydict['percent_waste_streams'] = 100.0 * no_tcp_waste_streams / float(no_tcp_streams)
    mydict['total_data_transfer'] = total_data_transfer
    mydict['total_data_waste'] = total_data_waste
    mydict['percent_data_waste'] = 100 * total_data_waste / float(total_data_transfer)
    mydict['total_dns_requests'] = len(dns_list)
    mydict['mean_dns_response_time'] = (sum(min(float(q[0]) for q in dns_list[k].responses) - min(float(q[0]) for q in dns_list[k].queries) for k in dns_list if dns_list[k].queries and dns_list[k].responses)) / len(dns_list)

    for k in d:
        l = len(d[k])
        xx = []
        o_ip = other(_myip, k)
        if ip_to_dns_id.has_key(o_ip):
            for dns_query_id in ip_to_dns_id[o_ip]:
                # print o_ip, dns_query_id, dns_list[dns_query_id].queries
                if dns_list[dns_query_id].queries and dns_list[dns_query_id].responses:
                    query_time = min(float(q[0]) for q in dns_list[dns_query_id].queries)
                    response_time = min(float(q[0]) for q in dns_list[dns_query_id].responses)
                    xx.append([response_time + 5, response_time, query_time, query_time - 5, 'DNS Query for ' + dns_list[dns_query_id].queries[0][3]])
        for v in d[k]:
            url1 = v[3]
            if(len(url1) > 0):
                url1 = url1[:50]
            xx.append([float(v[1]), float(v[1]), float(v[1]) + float(v[2]), float(v[1]) + float(v[2]), url1])
        xx += (maxlen - len(xx)) * [[0, 0, 0, 0, '']]
        ips.append(other(_myip, k))
        d2.append([other(_myip, k), xx])
    # print d2
    mydict['ips'] = sorted(ips)
    mydict['myip'] = myip[0] if len(myip) == 1 else "Could not be determined!"
    mydict['pcap_url'] = m.uploadedfile.url
    mydict['pcap_file'] = pcap_name
    mydict['csv_file'] = c + ".csv"
    mydict['csv_url'] = m.uploadedfile.url[:m.uploadedfile.url.rfind('.')] + '.csv'
    mydict['candle_sticks'] = d2

    ip_stats = []
    with open(csv2_path) as csv2_file:
        reader = csv.reader(csv2_file)
        for row in reader:
            ip1, ip2, transfer, startTime, duration = row
            ip_stats.append([other(_myip, [ip1, ip2]), transfer])

    mydict['ip_stats'] = ip_stats
    mydict['dns_list'] = dns_list.values()
    dnshosts = []

    def sign(x):
        return 0 if x == 0 else 1 if x > 0 else -1
    for dns in sorted(dns_list.values(), cmp=(lambda a, b: sign(min(float(q[0]) for q in a.queries) - min(float(q[0]) for q in b.queries)))):
        for host in dns.queryhosts:
            h = models.Host.objects.get_or_create(name=host)[0]
            h.updated = datetime.datetime.today()
            h.save()
            hp = models.HostPcap.objects.get_or_create(hostId=h, pcapId=m)[0]
            hp.save()
            sock_addrs = socket.gethostbyname_ex(host)[-1]
            for s in sock_addrs:
                i = models.HostIp.objects.get_or_create(hostId=h, ip=s)[0]
                i.save()
            s = sock_addrs[0]
            whois_result = whois(s)
            try:
                h.ip_range = whois_result['NetRange']
                h.org_name = whois_result['OrgName']
            except KeyError:
                try:
                    h.ip_range = whois_result['inetnum']
                    h.org_name = whois_result['role']
                except KeyError:
                    h.ip_range = "Could not be determined"
                    h.org_name = "Could not be determined"

            h.save()
            dnshosts.append(h)

    mydict['hosts'] = list(set(dnshosts))
    return render_to_response('pcap_analyze.html', mydict)


def map_traceroute(request, ip):
    output = "Beginning Traceroute to " + str(ip) + "..."
    mydict = {}
    mydict['output'] = output

    return render_to_response('maps.html', mydict)


def hosts_timestamp(request):
    x = ""
    try:
        x = max(host.updated for host in models.Host.objects.all())
    except Exception as e:
        print e
    return HttpResponse(str(x))


def hosts_list(request):
    hosts = models.Host.objects.all()
    mydict = {}
    hosts_set = list(set(hosts))
    for host in hosts_set:
        h_ips = models.HostIp.objects.filter(hostId=host)
        host.ips = ", ".join(h_ip.ip for h_ip in h_ips)
    mydict['hosts'] = hosts_set
    return render_to_response("hosts_list.html", mydict)


def hosts_detail(request, id):
    hostwebsites = models.HostPcap.objects.get(hostId=id)
    websites = (models.PcapFile.objects.get(pk=hw.pcapId) for hw in hostwebsites)
    return HttpResponse(json.dumps({"pcaps": list(website.shortfilename for website in websites)}))


def hosts_toggleBlocked(request, id):
    try:
        host = models.Host.objects.get(pk=id)
        print host.blocked
        host.blocked = not host.blocked
        host.updated = datetime.datetime.today()
        host.save()
    except Exception as e:
        print e
        pass
    return HttpResponse("")


def hosts_file(request):
    blocked_hosts = models.Host.objects.filter(blocked=True)
    hosts_begin = """
127.0.0.1 localhost

# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters

#Blocked Hosts begin:
"""
    return HttpResponse(hosts_begin + "\n".join("127.0.0.1 %s" % h.name for h in blocked_hosts))
