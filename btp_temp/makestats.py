import os, subprocess, csv, re
import glob
from collections import namedtuple
import math
import numpy as np
import matplotlib.mlab
import matplotlib.pyplot as plt


def apply(fns, values):
    return list(fns[i](values[i]) for i in xrange(len(fns)))


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




def makeStats(filename, csvpath, bandwidth_path):
    a, b = os.path.splitext(filename)
    csvpath = a + ".csv"
    all_streams_csvpath = a + "_all_streams.csv"
    csv2_path = a+"_ip.csv"
    cmd1 = "tshark -n -r %s -T fields -e tcp.stream"%(filename)
    cmd1_ip = "tshark -r %s -q -z conv,ip"%(filename)
    p = subprocess.Popen(cmd1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

    p_ip = subprocess.Popen(cmd1_ip, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    streams = sorted(list(set(map(int, filter(lambda x: len(x) > 0, map(lambda x: x.strip(), p.stdout.read().split('\n')))))))
    if not os.path.exists(csvpath) or not os.path.exists(all_streams_csvpath):
        with open(csvpath, "wb") as csvfile:
            with open(all_streams_csvpath, "wb") as all_streams_csvfile:
                writer = csv.writer(csvfile)
                all_streams_writer = csv.writer(all_streams_csvfile)
                for s in streams:
                    cmd2 = """tshark -r %s -q -z conv,tcp,tcp.stream==%d""" % (filename, s)
                    cmd3 = """tshark -n -R "tcp.stream==%d && http contains GET" -r %s -T fields -e http.request.full_uri """ % (s, filename)

                    q1 = subprocess.Popen(cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    q2 = subprocess.Popen(cmd3, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

                    l = q1.stdout.read().split("\n")[5]
                    m = re.match(r'\s*(\d+\.\d+\.\d+\.\d+):.*?\s+<->\s+(\d+\.\d+\.\d+\.\d+):.*?\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)\s+(.*?)\s+(.*?)\s+?', l)
                    ip1, ip2, transfer, startTime, duration = m.groups(0)

                    objects = map(lambda x: x.strip(), q2.stdout.read().strip().split('\n'))
                    num_objects = len(objects)
                    urls = ", ".join(objects)
                    url = "%d objects with url like %s..." % (num_objects, objects[0][:50])
                    if len(objects[0].strip()) == 0:
                        url = "No objects fetched"
                    writer.writerow([ip1, ip2, transfer, startTime, duration, url])
                    all_streams_writer.writerow([s, ip1, ip2, transfer, startTime, duration, num_objects, urls])
    if not os.path.exists(csv2_path):
        with open(csv2_path, 'wb') as csv2_file:
            writer = csv.writer(csv2_file)
            for line in p_ip.stdout.read().split("\n")[5:]:
                m = re.match(r'\s*(\d+\.\d+\.\d+\.\d+).*?\s+<->\s+(\d+\.\d+\.\d+\.\d+).*?\s+\d+\s+\d+\s+\d+\s+\d+\s+\d+\s+(\d+)\s+(.*?)\s+(.*?)\s+?', line)
                if not m:
                    continue
                ip1, ip2, transfer, startTime, duration = m.groups(0)
                writer.writerow([ip1, ip2, transfer, startTime, duration])
    # if not os.path.exists(bandwidth_path):
    #     cmd4 = """tshark -r %s -q -z io,stat,1""" % (filename)
    #     q4 = subprocess.Popen(cmd4, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    #     with open(bandwidth_path, 'w') as f:
    #         f.write(q4.stdout.read())


def makeBandwidthStats(filename, csvpath=None, bandwidth_path=None, bandwidth_uplink_path=None, bandwidth_downlink_path=None, retransmit_path=None, myip=None, debug=True):
    if debug:
        print "makeBandwidthStats: Beginning"
    if debug:
        print "makeBandwidthStats: Bandwidth"
    if bandwidth_path and not os.path.exists(bandwidth_path):
        cmd4 = """tshark -r %s -q -z io,stat,0.5""" % (filename)
        q4 = subprocess.Popen(cmd4, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        with open(bandwidth_path, 'w') as f:
            f.write(q4.stdout.read())
    if debug:
        print "makeBandwidthStats: Uplink Bandwidth"
    if bandwidth_uplink_path and not os.path.exists(bandwidth_uplink_path):
        cmd5 = """tshark -r %s -q -z io,stat,0.5,ip.src==%s""" % (filename, myip)  # uplink
        q5 = subprocess.Popen(cmd5, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        with open(bandwidth_uplink_path, 'w') as f:
            f.write(q5.stdout.read())
    if debug:
        print "makeBandwidthStats: Downlink Bandwidth"
    if bandwidth_downlink_path and not os.path.exists(bandwidth_downlink_path):
        cmd6 = """tshark -r %s -q -z io,stat,0.5,ip.dst==%s""" % (filename, myip)  # downlink
        q6 = subprocess.Popen(cmd6, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        with open(bandwidth_downlink_path, 'w') as f:
            f.write(q6.stdout.read())
    if debug:
        print "makeBandwidthStats: Retransmissions"
    if retransmit_path and not os.path.exists(retransmit_path):
        cmd7 = """tshark -r %s -R "tcp.analysis.retransmission" -T fields -e frame.time_relative""" % (filename)
        q7 = subprocess.Popen(cmd7, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        with open(retransmit_path, 'w') as f:
            f.write(q7.stdout.read())
    if debug:
        print "makeBandwidthStats: Finished"


def parse_bandwidth_data(bandwidth_path, threshold, retransmission_times):  # Threshold -- the speed that generally is available on mobile network.
    bandwidth_data = []
    with open(bandwidth_path) as f:
        lines = f.read().split("\n")[7:]
        for line in lines:
            match = re.match(r'\|\s+(.*?)\s+<>\s+(.*?)\s+\|\s+(.*?)\s+\|\s+(.*?)\s+\|', line)
            if match:
                startTime, endTime, frames, bytes = match.groups(0)
                endTime = (float(endTime))
                startTime = (float(startTime))
                no_retransmissions = len(filter(lambda x: True if float(startTime) <= x < float(endTime) else False, retransmission_times))
                bandwidth_data.append((startTime, endTime, int(frames), int(bytes), (float(bytes) / (float(endTime) - float(startTime)) / 1000.0), threshold, no_retransmissions*10))
    return bandwidth_data


def makeRttStats(filename, rtt_csv_path):
    if not os.path.exists(rtt_csv_path):
        cmd_rtt = """tshark -r %s -R "tcp.analysis.ack_rtt" -T fields -e frame.number -e frame.time_relative -e tcp.analysis.ack_rtt -E separator=, -E quote=n -E occurrence=f""" % (filename)
        p_rtt = subprocess.Popen(cmd_rtt, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        with open(rtt_csv_path, "w") as csv3_file:
            csv3_file.write(p_rtt.stdout.read())
    rtt_data = []
    with open(rtt_csv_path) as csv3_file:
        csvreader = csv.reader(csv3_file)
        for row in csvreader:
            rtt_data.append(apply([int, float, float], row))
    return rtt_data


def toi_normalized_analysis(pcap_name):
    name, ext = os.path.splitext(pcap_name)
    cmd1 = """tshark -r "%s" -R "dns.qry.name==timesofindia.indiatimes.com && dns.flags.response!=1" -T fields -e frame.time_relative""" % pcap_name
    p1 = subprocess.Popen(cmd1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    op = p1.stdout.read().strip().split("\n")[0].strip()  # first query
    # print "converting op to float, op =%s" % op
    # print "ord(op[0]) =", ord(op[0])
    toi_dns_query_time = float(str(op))

    normalized_pcap_name = name + "_normalized.pcap"
    cmd2 = """tshark -r "%s" -R "frame.time_relative >= %f" -F libpcap -w "%s" """ % (pcap_name, toi_dns_query_time, normalized_pcap_name)
    p2 = subprocess.Popen(cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    p2.stdout.read()

    cmd3 = """tshark -r "%s" -R "dns.qry.name==timesofindia.indiatimes.com && dns.flags.response==1" -T fields -e frame.time_relative""" % normalized_pcap_name
    p3 = subprocess.Popen(cmd3, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    op = p3.stdout.read().strip().split("\n")[0].strip()  # first response
    toi_dns_resp_time = float(op)

    cmd4 = """tshark -r "%s" -R "http contains GET && http.request.full_uri == \\"http://timesofindia.indiatimes.com/\\"" -T fields -e frame.time_relative -e ip.dst """ % (normalized_pcap_name)
    p4 = subprocess.Popen(cmd4, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    op = p4.stdout.read().strip().split()
    toi_homepage_get_request_time = float(op[0])
    toi_ip = op[1]

    cmd5 = """tshark -r "%s" -R "ip.dst==%s && tcp.flags.syn==1" -T fields -e frame.time_relative """ % (normalized_pcap_name, toi_ip)
    p5 = subprocess.Popen(cmd5, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    first_syn_time = float(p5.stdout.readline())

    cmd6 = """tshark -r "%s" -R "ip.dst==%s && tcp.flags.ack==1" -T fields -e frame.time_relative """ % (normalized_pcap_name, toi_ip)
    p6 = subprocess.Popen(cmd6, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    first_ack_time = float(p6.stdout.readline())

    tcp_handshake_time = first_ack_time - first_syn_time

    print toi_dns_resp_time, tcp_handshake_time, toi_homepage_get_request_time
    # makeStats(normalized_pcap_name, "", "%s_bandwidth.txt" % name)
    # getDNSPackets(normalized_pcap_name)


def open_subprocess(cmd):
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)


def meanvariance(l):
    s2 = 0
    s = 0
    l = map(float, l)
    for e in l:
        s += e
        s2 += e * e
    N = len(l)
    return (s/N, math.sqrt((s2 - (s*s)/N)/N))


class Website(object):
    __slots__ = ('name',
                 'first_dns_addr',
                 'first_get_addr',
                 'dns_lookup_time',
                 'tcp_handshake_time',
                 'redirection_time',
                 'peak_bandwidth',
                 # 'median_bandwidth',
                 'rtt_mean',
                 'rtt_std_deviation',
                 )

    def items(self):
        return [
            (field_name, getattr(self, field_name))
            for field_name in self.__slots__]

    def __iter__(self):
        for field_name in self.__slots__:
            yield getattr(self, field_name)

    def __getitem__(self, index):
        return getattr(self, self.__slots__[index])

    def __init__(self, *args):
        assert (len(self.__slots__) == len(args))
        for i in xrange(len(args)):
            setattr(self, self.__slots__[i], args[i])
        self.bandwidths = []

    def to_dict(self):
        d = dict()
        for s in self.__slots__:
            d[s] = getattr(self, s)
        return d

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return repr(self.to_dict())
def analyze_experiment_pcap(filename):
    name, ext = os.path.splitext(filename)

    bandwidth_path = name + "_bandwidth.txt"
    makeBandwidthStats(filename, None, bandwidth_path, debug=False)
    bandwidth_data = parse_bandwidth_data(bandwidth_path, 0, [])
    # print bandwidth_data
    rtt_csv_path = name + "_rtt.csv"
    rtt_stats = makeRttStats(filename, rtt_csv_path)
    # print rtt_stats
    cmd5 = """tshark -r %s -d tcp.port==8000,http -R "http.request.full_uri contains ""http://agni.iitd.ac.in:8000/wperf/idle_url?sleep_time="" " -T fields -e frame.number -e frame.time_relative """ % (filename)
    p5 = open_subprocess(cmd5)
    separator_times = list(apply([int, float], line.strip().split()) for line in p5.stdout.read().strip().split("\n"))
    separator_times = separator_times[1:]
    print separator_times

    class MToi(Website):
        def calculate_delays(self, filename, begin_frame, begin_time, end_frame, end_time):
            cmd1 = """tshark -r %s -R dns.qry.name==%s -c 1 -T fields -e frame.number -e frame.time_relative """ % (filename, self.first_dns_addr)
            # print cmd1
            p1 = open_subprocess(cmd1)
            first_dns_frame_no, first_dns_req_time = apply([int, float], p1.stdout.read().split())

            cmd2 = """tshark -r %s -R "frame.number>%d&&dns.resp.name==%s" -c 1 -T fields -e frame.number -e frame.time_relative """ % (filename, first_dns_frame_no, self.first_dns_addr)
            p2 = open_subprocess(cmd2)
            first_dns_resp_frame_no, first_dns_resp_time = apply([int, float], p2.stdout.read().split())

            self.dns_lookup_time = first_dns_resp_time - first_dns_req_time

            cmd3 = """tshark -r %s -R "http.request.full_uri==""%s""&&frame.number>%d" -c 1 -T fields -e frame.number -e frame.time_relative -e tcp.stream """ % (filename, self.first_get_addr, first_dns_resp_frame_no)
            p3 = open_subprocess(cmd3)
            first_get_frame, first_get_time, first_get_stream_no = apply([int, float, int], p3.stdout.read().split())

            cmd4 = """tshark -r %s -R "tcp.stream eq %d && tcp.flags.syn==1 && tcp.flags.ack==0" -c 1 -T fields -e frame.number -e frame.time_relative """ % (filename, first_get_stream_no)
            cmd5 = """tshark -r %s -R "tcp.stream eq %d && tcp.flags.syn==0 && tcp.flags.ack==1" -c 1 -T fields -e frame.number -e frame.time_relative """ % (filename, first_get_stream_no)
            p4 = open_subprocess(cmd4)
            p5 = open_subprocess(cmd5)
            first_syn_frame, first_syn_time = apply([int, float], p4.stdout.read().split())
            first_ack_frame, first_ack_time = apply([int, float], p5.stdout.read().split())

            self.tcp_handshake_time = first_ack_time - first_syn_time
            self.redirection_time = first_syn_time - first_dns_resp_time

    class DToi(Website):
        def calculate_delays(self, filename, begin_frame, begin_time, end_frame, end_time):
            cmd1 = """tshark -r %s -R "http.request.full_uri==""http://timesofindia.com/""&&frame.number>=%d" -c 1 -T fields -e frame.number -e frame.time_relative -e tcp.stream """ % (filename, begin_frame)
            p1 = open_subprocess(cmd1)
            first_try_stream_no = int(p1.stdout.read().split()[-1])
            # print first_try_stream_no
            cmd2 = """tshark -r %s -R "tcp.stream eq %d && tcp.flags.syn==1 && tcp.flags.ack==0 && frame.number>=%d" -c 1 -T fields -e frame.number -e frame.time_relative """ % (filename, first_try_stream_no, begin_frame)
            p2 = open_subprocess(cmd2)
            first_stream_syn_frane_no, first_stream_syn_time = apply([int, float], p2.stdout.read().split())

            cmd3 = """tshark -r %s -R "frame.number>=%d && dns.qry.name==""www.indiatimes.com"" " -c 1 -T fields -e frame.number -e frame.time_relative """ % (filename, first_stream_syn_frane_no)
            cmd4 = """tshark -r %s -R "frame.number>=%d && dns.resp.name==""www.indiatimes.com"" " -c 1 -T fields -e frame.number -e frame.time_relative """ % (filename, first_stream_syn_frane_no)
            p3 = open_subprocess(cmd3)
            p4 = open_subprocess(cmd4)
            dns_qry_time = float(p3.stdout.read().split()[-1])
            dns_resp_time = float(p4.stdout.read().split()[-1])
            self.dns_lookup_time = dns_resp_time - dns_qry_time
            delay1 = dns_qry_time - first_stream_syn_time

            cmd5 = """tshark -r %s -R "http.request.full_uri==""http://timesofindia.indiatimes.com/""&&frame.number>=%d" -c 1 -T fields -e frame.number -e frame.time_relative -e tcp.stream """ % (filename, first_stream_syn_frane_no)
            # print cmd5
            p5 = open_subprocess(cmd5)
            op = p5.stdout.read().split()
            # print op
            arbit, real_begin_time, good_stream_no = apply([int, float, int], (op))

            cmd4 = """tshark -r %s -R "tcp.stream eq %d && tcp.flags.syn==1 && tcp.flags.ack==0" -c 1 -T fields -e frame.number -e frame.time_relative """ % (filename, good_stream_no)
            cmd5 = """tshark -r %s -R "tcp.stream eq %d && tcp.flags.syn==0 && tcp.flags.ack==1" -c 1 -T fields -e frame.number -e frame.time_relative """ % (filename, good_stream_no)
            p4 = open_subprocess(cmd4)
            p5 = open_subprocess(cmd5)
            good_syn_frame, good_syn_time = apply([int, float], p4.stdout.read().split())
            good_ack_frame, good_ack_time = apply([int, float], p5.stdout.read().split())
            self.tcp_handshake_time = good_ack_time - good_syn_time
            self.redirection_time = delay1 + real_begin_time - dns_resp_time

    class MNytimes(MToi):
        pass

    class DNytimes(MToi):
        pass

    class MCricinfo(MToi):
        pass

    class DCricinfo(MToi):
        pass

    sites = [
        # MToi('m-toi', 'timesofindia.com', 'http://m.timesofindia.com/', 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        DToi('adblocked_toi', '', '', 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        DToi('toi', '', '', 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        # MNytimes('m-nytimes', 'www.nytimes.com', 'http://mobile.nytimes.com/', 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        # DNytimes('nytimes', 'www.nytimes.com', 'http://www.nytimes.com/', 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        # MCricinfo('m-cricinfo', 'www.cricinfo.com', 'http://m.espncricinfo.com/', 0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        # DCricinfo('cricinfo', 'www.cricinfo.com', 'http://www.espncricinfo.com/', 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    ]
    separator_times.append([1000000000, 1000000000])

    begin_frame, begin_time, [end_frame, end_time] =  0, 0, separator_times[0]
    bandwidth_ind, rtt_ind = 0, 0
    separator_ctr = 0
    while separator_ctr < len(separator_times):
        print "\t%s" % sites[separator_ctr].name
        # print "calculate delays for", sites[separator_ctr]
        sites[separator_ctr].calculate_delays(filename, begin_frame, begin_time, end_frame, end_time)

        bandwidths = []
        while(bandwidth_ind < len(bandwidth_data) and bandwidth_data[bandwidth_ind][1] <= end_time):
            bandwidths.append(bandwidth_data[bandwidth_ind][4])
            bandwidth_ind += 1
        sites[separator_ctr].bandwidths = bandwidths

        sites[separator_ctr].peak_bandwidth = max(bandwidths)
        sites[separator_ctr].median_bandwidth = 0  # calculate this one too!

        rtts = []
        while(rtt_ind < len(rtt_stats) and rtt_stats[rtt_ind][0] <= end_frame):
            rtts.append(rtt_stats[rtt_ind][-1])
            rtt_ind += 1

        sites[separator_ctr].rtt_mean, sites[separator_ctr].rtt_std_deviation = meanvariance(rtts) if rtts else (0, 0)

        # print sites[separator_ctr]
        separator_ctr += 1
        if separator_ctr != len(separator_times):

            begin_frame, begin_time, [end_frame, end_time] = end_frame, end_time, separator_times[separator_ctr]


        # max_bandwidth = max(a[4] for a in bandwidth_data if a[1] <= separator_times[0][1])
        # print max_bandwidth
    print sites
    with open(name + "_result.csv", "wb") as f:
        wr = csv.writer(f)
        slots = Website.__slots__
        wr.writerow(slots)
        for site in sites:
            # print list(getattr(site, slot) for slot in Website.__slots__)
            wr.writerow(list(getattr(site, slot) for slot in slots))
    return sites


def drange(start, stop, step):
    r = start
    while r < stop:
        yield r
        r += step


if __name__ == '__main__':
    sites = analyze_experiment_pcap("obs_25.pcap")
    print sites[0].bandwidths
    print sites[1].bandwidths

    without_ads_bw_cdf = list(sites[0].bandwidths)
    for i in xrange(1, len(without_ads_bw_cdf)):
        without_ads_bw_cdf[i] += without_ads_bw_cdf[i - 1]
    with_ads_bw_cdf = list(sites[1].bandwidths)
    for i in xrange(1, len(with_ads_bw_cdf)):
        with_ads_bw_cdf[i] += with_ads_bw_cdf[i - 1]
    m = max(len(without_ads_bw_cdf), len(with_ads_bw_cdf))
    x = list(drange(0, m*1.1, 0.5))
    p1 = plt.plot(x[:len(with_ads_bw_cdf)], with_ads_bw_cdf, label="with ads")
    p2 = plt.plot(x[:len(without_ads_bw_cdf)], without_ads_bw_cdf, label="without ads")
    plt.legend([p1, p2], ['With ads', 'Without Ads'], 'lower right')
    plt.show()


    # for fn in glob.glob("obs_pcaps\\*.pcap"):
    #     try:
    #         print fn
    #         analyze_experiment_pcap(fn)
    #     except Exception as e:
    #         pass
    #         # raise e


    # with open("obs_all.csv", "wb") as all_csv:
    #     title_row = None
    #     data_rows = []
    #     for fn in glob.glob("obs_pcaps\\*_result.csv"):
    #         with open(fn) as f:
    #             reader = csv.reader(f)
    #             rows = list(reader)
    #             # print rows
    #             if not title_row:
    #                 title_row = rows[0]
    #             data_rows += rows[1:]
    #     writer = csv.writer(all_csv)
    #     writer.writerow(title_row[3:])
    #     for row in data_rows:
    #         if '0.0' not in row:
    #             writer.writerow(row[3:])

    #PCA:
    # with open("obs_all.csv") as f:
    #     reader = csv.reader(f)
    #     rows = list(reader)
    #     r = np.array(rows[1:]).astype('float')
    #     print r.dtype
    #     p = matplotlib.mlab.PCA(r)
    #     print p





    # for fn in glob.glob("2013.04.11\\*"):
    #     if 'normalized' in fn:
    #         continue
    #     print fn
    #     try:
    #         toi_normalized_analysis(fn)
    #     except Exception as e:
    #         print e


    # toi_normalized_analysis("new\\shark_dump_all_blocked.pcap")
    # toi_normalized_analysis("new\\shark_dump_good_network.pcap")
    # toi_normalized_analysis("new\\shark_dump_room2.pcap")
    # toi_normalized_analysis("new\\shark_dump_bharti.pcap")
    # toi_normalized_analysis("new\\shark_dump_asl720.pcap")
    # for filename in ["shark_dump_asl720", "shark_dump_bharti", "shark_dump_esl", "shark_dump_room", "shark_dump_room2", "shark_dump_windT"]:
    #     print filename
    #     makeStats("new\\%s.pcap" % filename, "", "new\\%s_bandwidth.txt" % filename);
    #     getDNSPackets("new\\%s.pcap" % filename)
    # makeStats("toi_normal.pcap", "", "toi_normal_bandwidth.txt")
    # getDNSPackets("toi_normal.pcap")
    # makeStats("toi_cache_cleared.pcap", "", "toi_cache_cleared_bandwidth.txt")
    # getDNSPackets("toi_cache_cleared.pcap")
