# Standard Library Imports
import os
import re
import csv
import sys
import math
import json
import socket
import random
import urllib
import urllib2
import commands
import datetime
import threading
import subprocess

# django Imports
from django.views.decorators.csrf import csrf_exempt
from django.template import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import *
from django.core.urlresolvers import reverse
from django.core.exceptions import *
import models
import forms
import settings

#  Tornado Imports
import tornado.web
import tornado.websocket
# from tornado.options import options, define, parse_command_line

# Third Party Imports
# from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
# from matplotlib.figure import Figure
from HTMLParser import HTMLParser


def meanvariance(l):
    s2 = 0
    s = 0
    l = map(float, l)
    for e in l:
        s += e
        s2 += e * e
    N = len(l)
    return (s/N, math.sqrt((s2 - (s*s)/N)/N))


def ip_to_int(ip):
    try:
        parts = map(int, ip.split("."))
        x = (parts[0] << 24) + (parts[1] << 16) + (parts[2] << 8) + (parts[3])
        return x
    except:
        return -1


def int_to_ip(i):
    parts = []
    parts.insert(0, i % (1 << 8))
    i //= (1 << 8)
    parts.insert(0, i % (1 << 8))
    i //= (1 << 8)
    parts.insert(0, i % (1 << 8))
    i //= (1 << 8)
    parts.insert(0, i % (1 << 8))
    i //= (1 << 8)
    return ".".join(map(str, parts))


def whois(ip):
    p = subprocess.Popen(" ".join(["whois", ip]), stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    op = p.stdout.read()
    if op.find("Unknown AS number or IP network") == 0:
        print "UNKNOWN"
        h = urllib.urlopen("http://whois.net/ip-address-lookup/%s" % ip).read()

        class MYHTMLParser(HTMLParser):
            pre = False

            def handle_starttag(self, tag, attrs):
                if tag == "pre" and dict(attrs)['class'] == "bodyMed":
                    self.pre = True

            def handle_endtag(self, tag):
                self.pre = False

            def handle_data(self, data):
                if self.pre:
                    self.data = data
        # print h
        par = MYHTMLParser()
        par.feed(h)
        op = par.data

    result = {}
    for line in op.split("\n"):
        if len(line.strip()) == 0:
            continue
        if line[0] in ["#", "%", "["]:
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        result[k.strip()] = v.strip()
    if len(result.keys()) == 0:
        # Another format
        for line in op.split("\n"):
            if len(line.strip()) == 0:
                continue
            if line[0] in ["#", "%", "["]:
                continue
            else:
                b1, b2 = line.rfind("("), line.rfind(")")
                result['role'] = line[:b1].strip()
                result['inetnum'] = line[b2 + 1:].strip()
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
            w.testId = models.Test.objects.get(pk=int(pk))
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
        print "Writing dns file"
        cmd1 = """tshark -n -R "dns" -r %s""" % (filename)
        p = subprocess.Popen(cmd1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        with open(dnspath, 'w') as f:
            r = p.stdout.read()
            f.write(r)
        print "Done writing dns file"

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


def makeStats(filename, csvpath, bandwidth_path):
    print "makeStats: Beginning"
    a, b = os.path.splitext(filename)
    csvpath = a + ".csv"
    all_streams_csvpath = a + "_all_streams.csv"
    csv2_path = a + "_ip.csv"
    cmd1 = "tshark -n -r %s -T fields -e tcp.stream" % (filename)
    cmd1_ip = "tshark -r %s -q -z conv,ip" % (filename)
    p = subprocess.Popen(cmd1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    p_ip = subprocess.Popen(cmd1_ip, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    streams = sorted(list(set(map(int, filter(lambda x: len(x) > 0, map(lambda x: x.strip(), p.stdout.read().split('\n')))))))
    if not os.path.exists(csvpath) or not os.path.exists(all_streams_csvpath):
        print "makeStats: Writing stream csvs"
        with open(csvpath, "wb") as csvfile:
            with open(all_streams_csvpath, "wb") as all_streams_csvfile:
                writer = csv.writer(csvfile)
                all_streams_writer = csv.writer(all_streams_csvfile)
                stream_processes = {}
                for s in streams:
                    cmd2 = """tshark -r %s -q -z conv,tcp,tcp.stream==%d""" % (filename, s)
                    cmd3 = """tshark -n -R "tcp.stream==%d && http contains GET" -r %s -T fields -e http.request.full_uri -e frame.time_relative """ % (s, filename)

                    q1 = subprocess.Popen(cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    q2 = subprocess.Popen(cmd3, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    stream_processes[s] = [q1, q2]
                # for s in streams:
                    print "makeStats: Writing stream csvs (%d/%d)" % (s, streams[-1])
                    q1, q2 = stream_processes[s]
                    l = q1.stdout.read().split("\n")[5]
                    m = re.match(r'\s*(\d+\.\d+\.\d+\.\d+):.*?\s+<->\s+(\d+\.\d+\.\d+\.\d+):.*?\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)\s+(.*?)\s+(.*?)\s+', l + "  ")  # trailing space so that last \s+ can act as delimiter
                    ip1, ip2, transfer, startTime, duration = m.groups(0)

                    objects = map(lambda x: x, filter(lambda x: len(x) > 0, map(lambda x: x.strip(), q2.stdout.read().strip().split('\n'))))
                    objs = []
                    num_objects = len(objects)
                    for o in objects:
                        url, start_time = o.split()
                        objs.append("'%s'::%s" % (url, start_time))
                    urls = ", ".join(objs)
                    url = "%d objects" % num_objects
                    if num_objects > 0:
                        url += " with urls like: %s..." % objects[0][:50]
                    writer.writerow([ip1, ip2, transfer, startTime, duration, url])
                    all_streams_writer.writerow([s, ip1, ip2, transfer, startTime, duration, num_objects, urls])
    if not os.path.exists(csv2_path):
        print "makeStats: Writing ip csvs"
        with open(csv2_path, 'wb') as csv2_file:
            writer = csv.writer(csv2_file)
            for line in p_ip.stdout.read().split("\n")[5:]:
                m = re.match(r'\s*(\d+\.\d+\.\d+\.\d+).*?\s+<->\s+(\d+\.\d+\.\d+\.\d+).*?\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)\s+(.*?)\s+(.*?)\s+?', line)
                if not m:
                    continue
                ip1, ip2, transfer, startTime, duration = m.groups(0)
                writer.writerow([ip1, ip2, transfer, startTime, duration])
    print "makeStats: Finished"


def makeBandwidthStats(filename, csvpath, bandwidth_path, bandwidth_uplink_path, bandwidth_downlink_path, retransmit_path, myip):
    print "makeBandwidthStats: Beginning"
    print "makeBandwidthStats: Bandwidth"
    if not os.path.exists(bandwidth_path):
        cmd4 = """tshark -r %s -q -z io,stat,0.5""" % (filename)
        q4 = subprocess.Popen(cmd4, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        with open(bandwidth_path, 'w') as f:
            f.write(q4.stdout.read())
    print "makeBandwidthStats: Uplink Bandwidth"
    if not os.path.exists(bandwidth_uplink_path):
        cmd5 = """tshark -r %s -q -z io,stat,0.5,ip.src==%s""" % (filename, myip)  # uplink
        q5 = subprocess.Popen(cmd5, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        with open(bandwidth_uplink_path, 'w') as f:
            f.write(q5.stdout.read())
    print "makeBandwidthStats: Downlink Bandwidth"
    if not os.path.exists(bandwidth_downlink_path):
        cmd6 = """tshark -r %s -q -z io,stat,0.5,ip.dst==%s""" % (filename, myip)  # downlink
        q6 = subprocess.Popen(cmd6, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        with open(bandwidth_downlink_path, 'w') as f:
            f.write(q6.stdout.read())
    print "makeBandwidthStats: Retransmissions"
    if not os.path.exists(retransmit_path):
        cmd7 = """tshark -r %s -R "tcp.analysis.retransmission" -T fields -e frame.time_relative""" % (filename)
        q7 = subprocess.Popen(cmd7, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        with open(retransmit_path, 'w') as f:
            f.write(q7.stdout.read())
    print "makeBandwidthStats: Finished"


def intersect(l1, l2):
    return [x for x in l1 if x in l2] if l2 is not None else l1


def other(x, l):
    return l[1] if x == l[0] else l[0]


def get_org_from_ip(ip):
    try:
        i = ip_to_int(ip)
        orgs = models.Organization.objects.filter(lower__lt=i, higher__gt=i)
        if len(orgs) == 1:
            return orgs[0]
    except:
        pass
    s = ip
    whois_result = whois(s)
    ip_range, org_name = None, None
    try:
        ip_range = whois_result['NetRange']
        org_name = whois_result['OrgName']
    except KeyError:
        try:
            ip_range = whois_result['inetnum']
            org_name = whois_result['role']
        except KeyError:
            try:
                org_name = whois_result['person']
            except KeyError:
                print "Unknown Organization for ip : %s" % ip
                ip_range = "Unknown"
                org_name = "Unknown"
    org = None
    if not ip_range or ip_range == "Unknown":
        try:
            ip_range = whois_result['route']
            if "/" in ip_range:
                a, b = ip_range.split("/")
                a_int = ip_to_int(a)
                # begin = a_int & (1<<(32-int(b)))
                begin = a_int
                end = a_int | ((1 << (32 - int(b))) - 1)
                print int_to_ip(begin), int_to_ip(end)
                ip_range = "%s - %s" % (int_to_ip(begin), int_to_ip(end))
        except:
            pass
    if ip_range and org_name:
        hyphen = ip_range.find('-')
        lower, higher = ip_range[:hyphen].strip(), ip_range[hyphen + 1:].strip()
        lower_int, higher_int = map(ip_to_int, (lower, higher))
        org, org_created = models.Organization.objects.get_or_create(name=org_name, ip_range=ip_range, lower=lower_int, higher=higher_int)
        if org_created:
            org.save()
    return org


def pcap_analyze(request, pcap_name):
    mydict = {}
    m = models.PcapFile.objects.get(shortfilename=pcap_name)
    a, b = os.path.splitext(m.uploadedfile.path)
    c, d = os.path.splitext(pcap_name)
    harpath = a + ".har"
    if not os.path.exists(harpath):
        try:
            cmd = "python %s/main.py %s %s" % (settings.PCAP2HAR_LOC, m.uploadedfile.path, harpath)
            print cmd
            subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            print e
    csvpath = a + ".csv"
    csv2_path = a + "_ip.csv"
    csv3_path = a + "_rtt.csv"
    # csv4_path = a + "_streams.csv"
    all_streams_csvpath = a + "_all_streams.csv"
    bandwidth_path = a + "_bandwidth.txt"
    if not os.path.exists(csvpath) or not os.path.exists(csv2_path) or not os.path.exists(bandwidth_path) or not os.path.exists(all_streams_csvpath):
        makeStats(m.uploadedfile.path, csvpath, bandwidth_path)
    if True or not os.path.exists(csv3_path):
        cmd_rtt = "tshark -r %s -R 'tcp.analysis.ack_rtt' -T fields -e frame.time_relative -e tcp.analysis.ack_rtt -E separator=, -E quote=n -E occurrence=f" % (m.uploadedfile.path)
        p_rtt = subprocess.Popen(cmd_rtt, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        with open(csv3_path, "w") as csv3_file:
            csv3_file.write(p_rtt.stdout.read())
    rtt_data = []
    with open(csv3_path) as csv3_file:
        csvreader = csv.reader(csv3_file)
        for row in csvreader:
            rtt_data.append(row)

    mydict['rtt_data'] = rtt_data

    d = {}
    streams = []
    dns_list, ip_to_dns_id = getDNSPackets(m.uploadedfile.path)
    with open(csvpath) as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            streams.append(row)
            ip1, ip2, transfer, startTime, duration, url = row
            d.setdefault((ip1, ip2), [])
            d[(ip1, ip2)].append([transfer, startTime, duration, url])

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
        # l = len(d[k])
        xx = []
        o_ip = other(_myip, k)
        if o_ip in ip_to_dns_id:
            for dns_query_id in ip_to_dns_id[o_ip]:
                if dns_list[dns_query_id].queries and dns_list[dns_query_id].responses:
                    query_time = min(float(q[0]) for q in dns_list[dns_query_id].queries)
                    response_time = min(float(q[0]) for q in dns_list[dns_query_id].responses)
                    xx.append([response_time + 5, response_time, query_time, query_time - 5, 'DNS Qusadfadfery for ' + dns_list[dns_query_id].queries[0][3]])
        maxlen = max(maxlen, len(d[k]) + len(xx))

    stream_events = []  # opening/closing times

    for ind, stream in enumerate(streams):
        ip1, ip2, transfer, startTime, duration, url = stream
        startTime = float(startTime)
        duration = float(duration)
        stream_events.append((startTime, ind, other(_myip, [ip1, ip2]), 0))
        stream_events.append((startTime + duration, ind, other(_myip, [ip1, ip2]), 1))
    stream_events.sort(lambda x, y: (cmp(x[0], y[0])))
    no_streams_with_time = []
    no_toi_connections_with_time = []
    n = 0
    t = 0
    for stream_event in stream_events:
        if stream_event[-1] == 0:
            n += 1
            if stream_event[-2] in ["96.17.181.16", "96.17.181.27", "96.17.181.18"]:
                t += 1
        else:
            n -= 1
            if stream_event[-2] in ["96.17.181.16", "96.17.181.27", "96.17.181.18"]:
                t -= 1
        no_streams_with_time.append((stream_event[0], n))
        if stream_event[-2] in ["96.17.181.16", "96.17.181.27", "96.17.181.18"]:
            no_toi_connections_with_time.append((stream_event[0], t))
    mydict['no_streams_with_time'] = no_streams_with_time
    mydict['no_toi_connections_with_time'] = no_toi_connections_with_time
    mydict['no_ip_streams'] = no_ip_streams
    mydict['no_tcp_streams'] = no_tcp_streams
    mydict['no_tcp_waste_streams'] = no_tcp_waste_streams
    mydict['percent_waste_streams'] = 100.0 * no_tcp_waste_streams / float(no_tcp_streams)
    mydict['total_data_transfer'] = total_data_transfer
    mydict['total_data_waste'] = total_data_waste
    mydict['percent_data_waste'] = 100 * total_data_waste / float(total_data_transfer)
    mydict['total_dns_requests'] = len(dns_list)
    mydict['mean_dns_response_time'] = (sum(min(float(q[0]) for q in dns_list[k].responses) - min(float(q[0]) for q in dns_list[k].queries) for k in dns_list if dns_list[k].queries and dns_list[k].responses)) / len(dns_list)

    cmd1 = "tshark -n -r %s -T fields -e tcp.stream" % (m.uploadedfile.path)
    streams_data = {}
    p = subprocess.Popen(cmd1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    op = p.stdout.read()
    streams = sorted(list(set(map(int, filter(lambda x: len(x) > 0, map(lambda x: x.strip(), op.split('\n')))))))
    all_streams_data = []
    if False or all((not os.path.exists(a + "_streams_%d.csv" % i)) for i in xrange(11)):
        for s in streams:
            print "Writing Individual stream csvs: (%d/%d)" % (s, streams[-1])
            cmd_stream = "tshark -r %s -R 'tcp.analysis.ack_rtt and tcp.stream == %d' -T fields -e ip.dst -e tcp.analysis.ack_rtt -E separator=, -E quote=n -E occurrence=f" % (m.uploadedfile.path, s)
            p_stream = subprocess.Popen(cmd_stream, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stream_csv = a + "_streams_%d.csv" % s
            with open(stream_csv, 'w') as f:
                f.write(p_stream.stdout.read())

    for s in streams:
        stream_csv = a + "_streams_%d.csv" % s
        with open(stream_csv) as f:
            csvreader = csv.reader(f)
            streams_data.setdefault(s, ["", [], []])  # uplink, downlink
            for row in csvreader:
                if row[0] == _myip:
                    streams_data[s][2].append(row[1])
                else:
                    streams_data[s][0] = row[0]
                    streams_data[s][1].append(row[1])
    streams_stats = {}
    pingTimes = {'74.125.135.84': '1407.641', '122.160.242.176': '336.872', '50.19.220.231': '661.241', '96.17.182.43': '582.973', '96.17.182.42': '393.474', '96.17.182.65': '337.767', '96.17.182.66': '297.358', '96.17.182.40': '415.109', '184.30.50.110': '432.948', '74.125.236.31': '1465.920', '74.125.236.13': '336.650', '74.125.236.16': '348.960', '74.125.236.15': '1052.792', '204.236.220.251': '713.480', '74.125.236.9': '337.358', '118.214.111.144': '386.384', '96.17.182.10': '330.836', '96.17.182.17': '340.267', '96.17.182.50': '343.809', '2.18.147.206': '676.308', '96.17.182.74': '344.712', '31.13.79.23': '398.418', '96.17.182.58': '337.766', '107.20.164.42': '1697.474', '74.125.236.28': '315.357', '74.125.236.27': '338.574', '74.125.236.26': '1697.778', '74.125.236.25': '185.296', '199.59.148.86': '636.341', '107.20.176.85': '658.544', '23.35.84.211': '502.709', '184.30.63.139': '1673.310', '202.79.210.121': '1535.599'}

    def searchPingTime(ip):
        try:
            return float(pingTimes[ip])
        except:
            return 0
    for s in streams_data:
        if len(streams_data[s][0]) == 0 or len(streams_data[s][1]) == 0 or len(streams_data[s][2]) == 0:
            continue
        streams_stats.setdefault(s, ["", 0, 0, 0, 0, 0])  # ip, upstream-mean, upstream-variance, downstream-mean, downstream-variance, Ping time
        streams_stats[s][0] = streams_data[s][0]
        streams_stats[s][1:3] = meanvariance(streams_data[s][1])
        streams_stats[s][3:5] = meanvariance(streams_data[s][2])
        streams_stats[s][5] = searchPingTime(streams_stats[s][0])

    mydict['streams_stats'] = streams_stats.items()
    all_objects_data = []

    def short_url(url):
        return url if len(url) < 200 else (url[:50] + "...")
    with open(all_streams_csvpath) as all_streams_csvfile:
        reader = csv.reader(all_streams_csvfile)
        for row in reader:
            if int(row[6]) == 0:  # No objects downloaded
                continue
            urls_and_times = row[7].split(", ")
            url_starttime_list = []
            for ut in urls_and_times:
                url, start_time = ut.split("::")
                url_starttime_list.append((url[1:-1], float(start_time)))
            url_time_list = []
            for i, u_st in enumerate(url_starttime_list):
                url, starttime = u_st
                dt = 0
                if i == len(url_starttime_list) - 1:
                    dt = float(row[4]) + float(row[5]) - starttime
                else:
                    u2, st2 = url_starttime_list[i + 1]
                    dt = st2 - starttime

                url_time_list.append([row[0], short_url(url), url, starttime, dt])
            row.append(float(row[3]) / 1000 * float(row[5]))  # bandwidth
            try:
                row += streams_stats[int(row[0])]
            except KeyError:
                row += ([streams_data[s][0]] + (["No Data"] * 4) + [0])

            row.append(url_time_list)
            all_objects_data += url_time_list
            row[7] = list([x[1], x[2]] for x in url_time_list)
            all_streams_data.append(row)
    mydict['all_streams_data'] = all_streams_data
    mydict['all_objects_data'] = sorted(all_objects_data, cmp=lambda x, y: cmp(float(x[3]), float(y[3])))
    bandwidth_uplink_path = a + "_bandwidth_uplink.txt"
    bandwidth_downlink_path = a + "_bandwidth_downlink.txt"
    retransmit_path = a + "_retransmit.txt"
    makeBandwidthStats(m.uploadedfile.path, csvpath, bandwidth_path, bandwidth_uplink_path, bandwidth_downlink_path, retransmit_path, _myip)
    retransmission_times = []
    with open(retransmit_path) as retransmit_file:
        retransmission_times = map(float, retransmit_file.read().split())

    def parse_bandwidth_data(bandwidth_path, threshold, retransmission_times):  # Threshold -- the speed that generally is available on mobile network.
        bandwidth_data = []
        with open(bandwidth_path) as f:
            lines = f.read().split("\n")[7:]
            for line in lines:
                match = re.match(r'\|\s+(.*?)\s+<>\s+(.*?)\s+\|\s+(.*?)\s+\|\s+(.*?)\s+\|', line)
                if match:
                    startTime, endTime, frames, bytes = match.groups(0)
                    endTime = (float(endTime))
                    no_retransmissions = len(filter(lambda x: True if float(startTime) <= x < float(endTime) else False, retransmission_times))
                    bandwidth_data.append((startTime, endTime, frames, bytes, (float(bytes) / (float(endTime) - float(startTime)) / 1000.0), threshold, no_retransmissions*10))
        return bandwidth_data

    mydict['bandwidth_data'] = parse_bandwidth_data(bandwidth_path, m.uploadLimit + m.downloadLimit, retransmission_times)
    mydict['bandwidth_uplink_data'] = parse_bandwidth_data(bandwidth_uplink_path, m.uploadLimit, retransmission_times)
    mydict['bandwidth_downlink_data'] = parse_bandwidth_data(bandwidth_downlink_path, m.downloadLimit, retransmission_times)

    for k in d:
        # l = len(d[k])
        xx = []
        o_ip = other(_myip, k)
        if o_ip in ip_to_dns_id:
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
    mydict['HARVIEWER_URL'] = settings.HARVIEWER_URL
    mydict['har_url'] = m.uploadedfile.url[:-4] + "har"
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

    org_stats = {}
    for ip, transfer in ip_stats:
        org = get_org_from_ip(ip)
        org_stats.setdefault(org.name, [0, 0, 0])  # data transferred, streams, no. dns requests
        org_stats[org.name][0] += int(transfer)
    stream_stats = []
    with open(csvpath) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            ip1, ip2, transfer, startTime, duration, url = row
            stream_stats.append(other(_myip, [ip1, ip2]))
    for ip in stream_stats:
        on = get_org_from_ip(ip).name
        org_stats.setdefault(on, [0, 0, 0])
        org_stats[on][1] += 1

    mydict['ip_stats'] = ip_stats
    mydict['dns_list'] = dns_list.values()
    dnshosts = []

    def sign(x):
        return 0 if x == 0 else 1 if x > 0 else -1
    # for dns in sorted(dns_list.values(), cmp=(lambda a, b: sign(min(float(q[0]) for q in a.queries) - min(float(q[0]) for q in b.queries)))):
    for dns in dns_list.values():
        for host in dns.queryhosts:
            try:
                h = models.Host.objects.get(name=host)
                if h.org.name == "Unknown":
                    new_org = get_org_from_ip(h.hostip_set.all()[0].ip)
                    if new_org.name != "Unknown":
                        h.org = new_org
                        h.save()
            except ObjectDoesNotExist:
                sock_addrs = socket.gethostbyname_ex(host)[-1]
                s = sock_addrs[0]
                org = get_org_from_ip(s)
                h = models.Host.objects.create(org=org, stream_type=None, name=host)
                h.save()
                for s in sock_addrs:
                    i = models.HostIp.objects.get_or_create(hostId=h, ip=s)[0]
                    i.save()
            h.updated = datetime.datetime.today()
            h.save()
            hp = models.HostPcap.objects.get_or_create(hostId=h, pcapId=m)[0]
            hp.save()
            h.ips = ", ".join(s.ip for s in h.hostip_set.all())
            dnshosts.append(h)
    mydict['hosts'] = list(set(dnshosts))

    for h in mydict['hosts']:
        org_stats.setdefault(h.org.name, [0, 0,     0])
        org_stats[h.org.name][2] += 1

    mydict['org_stats'] = org_stats.items()
    return render_to_response('pcap_analyze.html', mydict)


def pcap_dnsquerylist(request, pcap_name):
    m = models.PcapFile.objects.get(shortfilename=pcap_name)
    dns_dict, ip_to_dns_id = getDNSPackets(m.uploadedfile.path)
    dns_list = dns_dict.values()
    dns_list.sort(lambda x, y: int((min(float(q[0]) for q in x.queries)) - (min(float(q[0]) for q in y.queries))))
    return HttpResponse("\n".join(d.queries[0][-1][2:] for d in dns_list))


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
        host.ips = ", ".join(s.ip for s in host.hostip_set.all())
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


def orgs_list(request):
    orgs = models.Organization.objects.all()
    for o in orgs:
        o.hosts = ", ".join(h.name for h in o.host_set.all())
    mydict = {}
    mydict['orgs'] = orgs
    return render_to_response("orgs_list.html", mydict)


class PcapAnalyzeHandler(tornado.web.RequestHandler):
    def get(self, pcap_name):
        self.write(pcap_analyze(None, pcap_name).content)


class State:
    START = 0
    AFTERDNS = 1
    AFTERSYN = 2


def dns_for_current_site(packet, cur_site):
    if not packet.haslayer(DNS):
        return False
    else:
        d = packet[DNS]
        if d.opcode != 0:  # 0 means query
            return False
        else:
            q = d.qd.qname
            if q.find(cur_site) == -1:
                return False
            else:
                return True


def psize(packet):
    #assume 20 from http://stackoverflow.com/questions/6639799/calculate-size-and-start-of-tcp-packet-data-excluding-header
    return packet[IP].len - packet[IP].ihl * 4 - 4 * packet[TCP].dataofs


def analyzeOneTest(packets, obsID, base):  # base is just for debugging
    print "observation id:", obsID
    agniIP = "180.149.52.3"
    NEAR_ENOUGH = 20
    sites = ['facebook', 'twitter', 'quora', 'timesofindia', 'nytimes', 'bbc.co.uk',  'cricinfo', 'amazon', 'dailymotion', 'tumblr']
    data = {}
    dnsinds = [index for index in xrange(len(packets)) if packets[index].haslayer(DNS)]
    state = State.START
    dnsstarttime = 0
    dnsendtime = 0
    handshakestarttime = 0
    handshakeendtime = 0
    tcp_handshake_time = 0
    pagesize = 0
    cur_ind = 0
    # processing_url = sites[cur_ind]
    ind = 0
    dns_index = 0
    while ind < len(packets):
        if state == State.START:
            while packets[dnsinds[dns_index]][DNS].qd.qname.find(sites[cur_ind]) == -1:
                dns_index += 1
            ind = dnsinds[dns_index]
            state = State.AFTERDNS
        elif state == State.AFTERDNS:
            print "site= ", sites[cur_ind], "dns start packet: ", dnsinds[dns_index] + base
            dnsstarttime = packets[dnsinds[dns_index]].time
            while dnsinds[dns_index + 1] - dnsinds[dns_index] <= NEAR_ENOUGH and packets[dnsinds[dns_index]][DNS].qd.qname.find(sites[cur_ind]) != -1:
                dns_index += 1
            print "last dns packet: ", dnsinds[dns_index] + base
            cur_ind += 1
            for pk in xrange(dnsinds[dns_index] + 1, len(packets)):
                packet = packets[pk]
                if packet.haslayer(TCP) and packet[TCP].flags == 2:  # 2== syn packet
                    dnsendtime = packet.time
                    state = State.AFTERSYN
                    ind = pk
                    print "Syn found at packet no:", ind + base
                    break
                continue
        elif state == State.AFTERSYN:
            pack = packets[ind]
            handshakestarttime = pack.time
            for pk in xrange(ind, len(packets)):
                packet = packets[pk]
                if packet.haslayer(TCP) and packet[TCP].flags == 0x10 and packet[IP].src == pack[IP].dst and packet[IP].dst == pack[IP].src:  # flag==0x10 means ACK
                    handshakeendtime = packet.time
                    tcp_handshake_time = handshakeendtime - handshakestarttime
                    state = State.AFTERDNS
                    next_dns_site = sites[cur_ind] if cur_ind < len(sites) else "agni"
                    while dns_index < len(dnsinds) and packets[dnsinds[dns_index]][DNS].qd.qname.find(next_dns_site) == -1:
                        dns_index += 1
                    max_ind = dnsinds[dns_index]
                    if cur_ind == len(sites):
                        for p in xrange(ind, len(packets)):
                            p1 = packets[p]
                            if p1.haslayer(TCP) and p1[IP].src == pack[IP].src and p1[IP].dst == agniIP:
                                max_ind = p
                                break
                    pagesize = sum(psize(packets[j]) for j in xrange(pk, max_ind) if packets[j].haslayer(TCP) and packets[j][IP].dst == pack[IP].src)
                    data[sites[cur_ind-1]] = {'dnsTime': dnsendtime - dnsstarttime, 'pageTotalSize': pagesize, 'tcpHandshakeTime': tcp_handshake_time}
                    break
                continue
            if cur_ind == len(sites):
                print data
                break


def analyzePcap(pcap):
    packets = rdpcap(pcap)
    agniIP = "180.149.52.3"
    fromAgniInds = [index for index in xrange(len(packets)) if packets[index].haslayer(Raw) and packets[index][IP].src == agniIP]
    idpackets = []
    for i in fromAgniInds:
        packet = packets[i]
        load = packet[Raw].load
        data = load.split("\n")[-1]
        m = re.match(r'id:(\d+)', data)
        if m:
            idpackets.append((i, int(m.group(1))))
    for ind, obsId in idpackets:
        analyzeOneTest(packets[ind:], obsId, ind)


class PcapProgressHandler(tornado.websocket.WebSocketHandler):
    def open(self, shortfilename):
        m = models.UploadedFile.objects.get(shortfilename=shortfilename)
        fieldfile = m.uploadedfile   # https://docs.djangoproject.com/en/dev/ref/models/fields/#filefield-and-fieldfile
        with open(fieldfile.path):
            pass

    def notify(self, text, prog):
        self.write_message("{\"Log\":\"%s\",\"prog\":\"%d\"}" % (text, prog))


class TracerouteHandler(tornado.websocket.WebSocketHandler):
    def open(self, ip):
        self.p = subprocess.Popen(['traceroute', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        t = threading.Thread(target=(lambda: self.send_output()))
        t.daemon = True
        t.start()

    def send_output(self):
        while self.p.poll() is None:  # running
            line = self.p.stdout.readline()
            if line is not None and len(line) > 0:
                self.write_message(json.dumps({'stdout': line}))
        self.write_message(json.dumps({'stdout': 'Done! For red marked ip addresses, the location couldn\'t be determined with <a href="http://hostip.info">hostip.info</a>. If you know the correct location, please update it there.'}))


class GeoIpHandler(tornado.web.RequestHandler):
    """Gives Location for a given IP. Using http://www.geoiptool.com/"""
    def find_val(self, data, key):
        a = data[data.find(key):]
        b = a[a.find("\n"):]
        c = b[b.find(">"):]
        e = c[:c.find("\n")]
        d = e.rfind("<")
        return c[1:d], c[d:]

    def get(self, ip):
        wp = urllib.urlopen("http://www.geoiptool.com/en/?IP=%s" % ip).read()
        op = {}
        op['host_name'], wp = self.find_val(wp, "Host Name:")
        op['ip_address'], wp = self.find_val(wp, "IP Address:")
        country, wp = self.find_val(wp, "Country:")
        x = country[country.find(">"):]
        x = x[:x.find("<")]
        op['country'] = x[1:].strip()
        op['city'], wp = self.find_val(wp, "City:")
        op['longitude'], wp = self.find_val(wp, "Longitude:")
        op['latitude'], wp = self.find_val(wp, "Latitude:")
        self.write(json.dumps(op))

