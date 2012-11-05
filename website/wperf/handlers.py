from tornado.options import options, define, parse_command_line
import tornado.web,tornado.websocket
import models
import settings
import re,subprocess,json
from scapy.all import *
class State:
  START=0
  AFTERDNS=1
  AFTERSYN=2

def dns_for_current_site(packet,cur_site):
  if not packet.haslayer(DNS):
    return False
  else:
    d=packet[DNS]
    if d.opcode!=0: #0 means query
      return False
    else:
      q=d.qd.qname
      if q.find(cur_site)==-1:
        return False
      else:
        return True


def psize(packet):
  #assume 20 from http://stackoverflow.com/questions/6639799/calculate-size-and-start-of-tcp-packet-data-excluding-header
  return packet[IP].len-packet[IP].ihl*4-4*packet[TCP].dataofs
def analyzeOneTest(packets,obsID,base): # base is just for debugging
  print "observation id:",obsID
  agniIP="180.149.52.3"
  NEAR_ENOUGH=20
  sites=['facebook', 'twitter', 'quora','timesofindia','nytimes','bbc.co.uk', 'cricinfo','amazon','dailymotion','tumblr' ]
  data={}
  dnsinds=[index for index in xrange(len(packets)) if packets[index].haslayer(DNS)]
  state=State.START
  dnsstarttime=0; dnsendtime=0; handshakestarttime=0; handshakeendtime=0; pagesize=0
  cur_ind=0
  processing_url=sites[cur_ind]
  ind=0
  dns_index=0
  while ind<len(packets):
    if state==State.START:
      while packets[dnsinds[dns_index]][DNS].qd.qname.find(sites[cur_ind])==-1:
        dns_index+=1
      ind=dnsinds[dns_index]
      state=State.AFTERDNS
    elif state==State.AFTERDNS:
      print "site= ",sites[cur_ind], "dns start packet: ",dnsinds[dns_index]+base
      dnsstarttime=packets[dnsinds[dns_index]].time
      while dnsinds[dns_index+1]-dnsinds[dns_index]<=NEAR_ENOUGH and packets[dnsinds[dns_index]][DNS].qd.qname.find(sites[cur_ind])!=-1:
        dns_index+=1
      print "last dns packet: ", dnsinds[dns_index]+base
      cur_ind+=1
      for pk in xrange(dnsinds[dns_index]+1, len(packets)):
        packet=packets[pk]
        if packet.haslayer(TCP) and packet[TCP].flags==2: #2== syn packet
          dnsendtime=packet.time
          state=State.AFTERSYN
          ind=pk
          print "Syn found at packet no:",ind+base
          break
        continue
    elif state==State.AFTERSYN:
      pack=packets[ind]
      handshakestarttime=pack.time
      for pk in xrange(ind,len(packets)):
        packet=packets[pk]
        if packet.haslayer(TCP) and packet[TCP].flags==0x10 and  packet[IP].src==pack[IP].dst and packet[IP].dst==pack[IP].src: #flag==0x10 means ACK
          handshakeendtime=packet.time
          state=State.AFTERDNS
          next_dns_site=sites[cur_ind] if cur_ind<len(sites) else "agni"
          while dns_index<len(dnsinds) and packets[dnsinds[dns_index]][DNS].qd.qname.find(next_dns_site)==-1:
            dns_index+=1
          max_ind=dnsinds[dns_index]
          if cur_ind==len(sites):
            for p in xrange(ind, len(packets)):
              p1=packets[p]
              if p1.haslayer(TCP) and p1[IP].src==pack[IP].src and p1[IP].dst==agniIP:
                max_ind=p
                break;
          pagesize=sum(psize(packets[j]) for j in xrange(pk,max_ind) if packets[j].haslayer(TCP) and packets[j][IP].dst==pack[IP].src)
          data[sites[cur_ind-1]]={'dnsTime':dnsendtime-dnsstarttime, 'pageTotalSize':pagesize}
          break
        continue
      if cur_ind==len(sites):
        print data
        break
def analyzePcap(pcap):
  packets=rdpcap(pcap)
  agniIP="180.149.52.3"
  fromAgniInds=[index for index in xrange(len(packets)) if packets[index].haslayer(Raw) and packets[index][IP].src==agniIP]
  idpackets=[]
  for i in fromAgniInds:
    packet=packets[i]
    load=packet[Raw].load
    data=load.split("\n")[-1]
    m=re.match(r'id:(\d+)', data)
    if m:
      idpackets.append((i, int(m.group(1))))
  for ind,obsId in idpackets:
    analyzeOneTest(packets[ind:], obsId, ind)


class PcapProgressHandler(tornado.websocket.WebSocketHandler):
  def open(self,shortfilename):
    m=models.UploadedFile.objects.get(shortfilename=shortfilename)
    fieldfile=m.uploadedfile  #https://docs.djangoproject.com/en/dev/ref/models/fields/#filefield-and-fieldfile
    with open(fieldfile.path) as f:
      pass


  def notify(self,text,prog):
    self.write_message("{\"Log\":\"%s\",\"prog\":\"%d\"}"%(text,prog))


class TracerouteHandler(tornado.websocket.WebSocketHandler):
  def open(self,ip):
    p = subprocess.Popen(['traceroute',ip],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while p.poll() is None: #running
      line=p.stdout.readline()
      if line!=None and len(line)>0:
        self.write_message(json.dumps({'stdout':line})) 
    self.write_message(json.dumps({'stdout':'Done! For red marked ip addresses, the location couldn\'t be determined with <a href="http://hostip.info">hostip.info</a>. If you know the correct location, please update it there.'}))

if __name__=="__main__":
  analyzePcap('proper.pcap')
