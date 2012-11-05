import datetime,pytz
import rpy2.robjects as robjects
from datetime import date
import pcapy
import dpkt
import os
import sys
import socket
import models
from django.template import *
from django.shortcuts import render_to_response
from django.http import *
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import  matplotlib.pyplot as plt
r=robjects.r;
# great documentation at http://www.commercialventvac.com/dpkt.html
#download youtube-dl from the repos and then run youtube-dl -U to update it, then use the -g flag to download the video
vidctr=0;
def grab():
  # Arguments here are:
  #   device
  #   snaplen (maximum number of bytes to capture _per_packet_)
  #   promiscious mode (1 for true)
  #   timeout (in milliseconds)
  unprocpackets=[]
  cap = pcapy.open_live('eth0', 10000, 1, 0)

  # Read packets -- header contains information about the data from pcap,
  # payload is the actual packet as a string
  (header, payload) = cap.next()
  capture=True
  while capture:
    try:
      eth = dpkt.ethernet.Ethernet(str(payload))
      ip = eth.data
      if (ip.__dict__).has_key('tcp'):
        tcp=ip.data
        pckt={}
        pckt['src_ip']=socket.inet_ntoa(ip.src)
        pckt['dst_ip']=socket.inet_ntoa(ip.dst)
        pckt['src_port']=tcp.sport
        pckt['dst_port']=tcp.dport
        pckt['timestamp']=datetime.datetime.now()
        pckt['seqno']=tcp.seq
        pckt['ackno']=tcp.ack
        pckt['datalen']=len(tcp.data)
        pckt['window_size']=tcp.win
        pckt['fin'] = ( tcp.flags & dpkt.tcp.TH_FIN ) != 0
        pckt['syn'] = ( tcp.flags & dpkt.tcp.TH_SYN ) != 0
        pckt['urg']= (tcp.flags& dpkt.tcp.TH_URG)
        pckt['ack']= (tcp.flags& dpkt.tcp.TH_ACK)
        pckt['push']= (tcp.flags& dpkt.tcp.TH_PUSH)
        pckt['rst']= (tcp.flags& dpkt.tcp.TH_RST)
        unprocpackets.append(pckt)
      (header, payload) = cap.next() #move to the next packet
    except KeyboardInterrupt as e:
      capture=False
    except Exception as e:
      print "Problem in capturing packets" +str(e)

#lets divide the packets into lists based on target ip and port and sourceip and port
  connections=[]
  for pckt in unprocpackets:
    newconn=True
    for i in range(0,len(connections)):
      if ((connections[i])[0][2])==pckt['src_ip'] and connections[i][0][0]==pckt['dst_ip'] and connections[i][0][3]==pckt['src_port'] and connections[i][0][1]==pckt['dst_port']:
        connections[i][1].append(pckt)
        newconn=False
      if connections[i][0][2]==pckt['dst_ip'] and connections[i][0][0]==pckt['src_ip'] and connections[i][0][3]==pckt['dst_port'] and connections[i][0][1]==pckt['src_port']:
        connections[i][1].append(pckt)
        newconn=False
    if newconn:
      print "Found new Connection "
      print str(pckt['src_port'])
      print str(pckt['dst_port'])
      print str(pckt['src_ip'])
      print str(pckt['dst_ip'])
      print "................"
      connections.append([[pckt['dst_ip'],pckt['dst_port'],pckt['src_ip'],pckt['src_port']],[pckt]]) #note here that first packet will be initiated by our computer

  ytconn=[[],[]]
  for conn in connections:
    if len(conn[1])>len(ytconn[1]):
      ytconn=conn



  #creating a connection
  tcon=models.TcpConn()
  tcon.src_ip=ytconn[0][2]
  tcon.dst_ip=ytconn[0][0]
  tcon.dst_port=ytconn[0][1]
  tcon.src_port=ytconn[0][3]
  if str(tcon.src_ip)!=raw_input("Enter your ip address\n"):
    tcon.src_ip=ytconn[0][0]
    tcon.dst_ip=ytconn[0][2]
    tcon.dst_port=ytconn[0][3]
    tcon.src_port=ytconn[0][1]
#ask additional details.
  tcon.url=raw_input("Video URL: ")
  tcon.quality=raw_input("Quality: ")
  tcon.vidlen=int(raw_input("Length of Video(in secs): "))
  tcon.save() #save the connection

#filter the packets
  packets=ytconn[1]
  print "Finishsed filtering packets, now storing in the database.Number of collected packets Collected Packets: "+str(len(packets))
  #packets.reverse()

  for pckt in packets: #add the connection id to all the packets  and save them
    packet=models.TcpPacket()
    packet.tcpConn=tcon
    packet.src2dst=(pckt['src_ip']==tcon.src_ip)
    packet.timestamp=pckt['timestamp']
    packet.seqno=pckt['seqno']
    packet.ackno=pckt['ackno']
    packet.window_size=pckt['window_size']
    packet.urg=pckt['urg']
    packet.ack=pckt['ack']
    packet.push=pckt['push']
    packet.rst=pckt['rst']
    packet.syn=pckt['syn']
    packet.fin=pckt['fin']
    packet.datalen=pckt['datalen']
    packet.save()

def homepage(request):
  entries=models.TcpConn.objects.all().order_by('id')
  mydict={'entries':entries}
  return render_to_response('index.html',mydict)



def rate(request):
  videos=['pE12H1HorUU', '4oAB83Z1ydE', 'DD-2MQMNlMw', 'sBrsM_WlfV8','pE12H1HorUU','5Tp1hbf_y2E','X66PDW1Mjf8','UV3RflsNxak','XplBCNMUu6s', '-mDlEqdKe0g','9cqABojhqr4','R5Nwnqz_iEY','Jg1ISNSXZHY','_2lzmHXcvR0','b3HeLs8Yosw','jUe8uoKdHao','mgEixhE3Oms','gXd_1S_2UBk','8c2ahBlTPz0','PHrwkVoTcHc',
     'J7E-aoXLZGY','5voP_K2aI3A','jM9s_A4PL5o','5LOcUkm8m9w','injlNuvSXMY','FPAa7BqgSbw','EHIpVVzzJpA','elKxgsrJFhw','tWtqEp2YMVI','iwmG43D0vD4','kiLCmstyDdM','VUlwlRW5Y34','VZkisUjcnsc','YWuJ11RaB6g','m0wVC3CLLn4','DVb36cOnScY','yiWqyJOTJfU','7tVdhoi9MTw','tOwPgmhSoAw','UiLSiqyDf4Y','Y_UmWdcTrrc','rznYifPHxDg','Bz_KbDbtbnc','UdVtIsipY5E','BQDYt61yHdg','6fhywUYu9zM','vO8aTlqRjiw','HGWNJ_3vQ3A','8yMuu2QG9ss','1Y_wJR1I-9s','9JM4oLSTRdk','cPGBmVEGfes','1vpBOH2gf-k','5XFhVtB9j3Q','e4yseHzHoxI','iAshrU2i7HQ' ]
  vidid = request.GET.get('v')
  ctr=models.Counter.objects.get(pk=1);
  ctr.val = (ctr.val+1)%len(videos)
  ctr.save()
  return render_to_response('rate.html',{'v':(videos[ctr.val]), 'phoneConf':int(request.GET.get('phoneConf'))})



def description(request):
  return render_to_response('description.html',{})

def analysis(request):
  traceid=int(request.GET.get('id'))
  #getStatVaritations(traceid)
  threshold=float(request.GET.get('threshold'))
  conn=models.TcpConn.objects.get(pk=traceid)
#get all packets for the trace
#  pkts=models.TcpPacket.objects.all().filter(tcpConn=conn)
  mydict={}
  #mydict['imgs']=['/static/vperf_extrabuff.png','/static/vperf_playloc.png','/static/vperf_acks.png','/static/vperf_datareqd.png']
  mydict['imgs']=['/static/vperf_extrabuff.png','/static/vperf_playloc.png','/static/vperf_acks.png']
  mydict['stats']= graph(threshold,traceid)
  mydict['conn']=conn
  return render_to_response('analysis.html',mydict)

def getStatVaritations(request):
  traceid=int(request.GET.get('id'))
  frebuf=[]
  tinit=[]
  trebuf= []
  threshold=[]
  qoe=[]
  for i in range(1,20):
    x=graph(1.0*i,traceid)
    frebuf.append(x['F_rebuf'])
    tinit.append(x['T_init'])
    trebuf.append(x['T_rebuf'])
    qoe.append(getQoe(-1,x['T_init'],x['F_rebuf'],x['T_rebuf'],x['vidlen']))
    threshold.append(i)
  fig=Figure()
  ax=fig.add_subplot(111,xlabel="Threshold",ylabel="Freq rebuf",title="Frequency of Rebuffering",xlim=[min(threshold),max(threshold)],ylim=[min(frebuf),max(frebuf)])
  ax.plot(threshold,frebuf,"rs-")
  canvas=FigureCanvas(fig)
  canvas.print_figure(os.getcwd()+"/Video_Performance/static/vperf_frebuf.png")

  fig2=Figure()
  ax=fig2.add_subplot(111,xlabel="Threshold",ylabel="T initial",title="Time to start playing video",xlim=[min(threshold),max(threshold)],ylim=[min(tinit),max(tinit)])
  ax.plot(threshold,tinit,"rs-")
  canvas2=FigureCanvas(fig2)
  canvas2.print_figure(os.getcwd()+"/Video_Performance/static/vperf_tinit.png")

  fig3=Figure()
  ax=fig3.add_subplot(111,xlabel="Threshold",ylabel="Time rebuf",title="Time in Rebuffering",xlim=[min(threshold),max(threshold)],ylim=[min(trebuf),max(trebuf)])
  ax.plot(threshold,trebuf,"rs-")
  canvas3=FigureCanvas(fig3)
  canvas3.print_figure(os.getcwd()+"/Video_Performance/static/vperf_trebuf.png")


  fig4=Figure()
  ax=fig4.add_subplot(111,xlabel="Threshold",ylabel="QoE",title="Quality of Experience",xlim=[min(threshold),max(threshold)],ylim=[min(qoe),max(qoe)])
  ax.plot(threshold,qoe,"rs-")
  canvas4=FigureCanvas(fig4)
  canvas4.print_figure(os.getcwd()+"/Video_Performance/static/vperf_qoe.png")

  mydict={}
  mydict['imgs']=['/static/vperf_frebuf.png','/static/vperf_trebuf.png','/static/vperf_tinit.png','/static/vperf_qoe.png']
  conn=models.TcpConn.objects.get(pk=traceid)
  mydict['conn']=conn
  return render_to_response('stats.html',mydict)


def graph(threshold,traceid):
  if threshold==0.0:
    threshold=0.01 # we are dividing by threshold in the simulator main loop and so need to have non zero value of threshold
  conn=models.TcpConn.objects.get(pk=traceid)
  pkts=models.TcpPacket.objects.all().filter(tcpConn=conn).order_by('timestamp') #get all packets for the trace in the order they were received
  stats={}
  stats["Threshold Value"]=threshold

#create a graph for playloc
  ratesamples=models.PlayDataReq.objects.all().filter(tcpConn=conn) #get all buffrate for the trace in the order they were received
  vidtime=[]
  datareqd=[]
  for smpl in ratesamples:
    vidtime.append(smpl.playLoc)
    datareqd.append(smpl.playData)


#simulate the video viewing
  realtime=[]
  acks=[]
#time 0 is when we send syn for startiing connection
  def total_seconds(td):
    return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 1e6) / 1e6

  for pkt in pkts:
    if pkt.src2dst and pkt.ack and pkt.ackno>0:
      print pkt.timestamp
      realtime.append(total_seconds((pkt.timestamp-pkts[0].timestamp)))
      acks.append(pkt.ackno)
      stats['time'] = pkt.timestamp


  ymin=min(acks)
  stats['Video_Size']=str((max(acks)-ymin)/1000)+" KBytes"
  stats['Average_Speed']=str((max(acks)-ymin)/(1000*(max(realtime))))+ " KBytes/sec"
  stats['vidlen']=conn.vidlen

  for i in range(0,len(acks)):
    acks[i]=acks[i]-ymin

#here i have translated the realtime and the data axis to my requirement and they have values in seconds
  extrabuff=acks[0]
  playloc=0 #time till the video has been played
  totlen=conn.vidlen
  totsize=max(acks)-min(acks)
#There are several ways to model the video playrate. The most naive of these methods is to simply assume a constant play rate and model it. A more complicated model finds the playrate close to the point of play and then tries to ACTUALLY play the video. THe second is what we will be attempting here.
  #vidplayrate=totsize/totlen #the number of bits played per second
#initialise
  if len(datareqd)==0:
    datareqd.append(0)
    vidtime.append(0)
    datareqd.append(totsize)
    vidtime.append(max(realtime))
  def getClosestTime(loc,vidtime):
    pos=0
    for i in range(0,len(vidtime)-2):
      pos = i
      if vidtime[i]>loc:
        break
    if ((vidtime[pos]-loc)<(loc-vidtime[pos-1])):
      return pos
    else:
      return pos-1

  def getExtraBuffReqd(start,end,vidtime,datareqd):
    if start> conn.vidlen:
      return sys.maxint
    start_close=getClosestTime(start,vidtime)
    end_close=getClosestTime(end,vidtime)
    #print "start time",start,"start close",vidtime[start_close],"end",end,"end_close",vidtime[end_close],"ans",(datareqd[end_close]-datareqd[start_close])
    retval=(datareqd[end_close]-datareqd[start_close])*(totsize/datareqd[-1])
    if ((retval==0)and (end_close<len(datareqd)-1)):
      retval=(datareqd[end_close+1]-datareqd[start_close])*(totsize/datareqd[-1])
    if start_close==end_close:
      retval=((end-start)/totlen)*(totsize)
    return retval

  sim_realtime=[]
  sim_acks=[]
  sim_playloc=[]
  sim_extrabuff=[]
  sim_realtime.append(realtime[0])
  sim_acks.append(acks[0])
  sim_playloc.append(0)
  sim_extrabuff.append(0)
  stats['N_rebuf']=0
  timebufferedup=0;
#and then spin

  for i in range(1,len(realtime)):
    extrabuff+=acks[i]-acks[i-1]
    reqdbuff=getExtraBuffReqd(playloc,playloc+threshold,vidtime,datareqd)
    if extrabuff>reqdbuff:
      timebufferedup=playloc+threshold
    if timebufferedup>=playloc+realtime[i]-realtime[i-1]:
#lets play some video then for the entire time duration of realtime[i]-realtime[i-1]
      #if extrabuff>getExtraBuffReqd(realtime[i],realtime[i-1]):
      extrabuff-=reqdbuff*(realtime[i]-realtime[i-1])/threshold
      playloc+=(realtime[i]-realtime[i-1])
      sim_realtime.append(realtime[i])
      sim_acks.append(acks[i])
      sim_playloc.append(playloc)
      sim_extrabuff.append(extrabuff)
    else:
      sim_realtime.append(realtime[i])
      sim_acks.append(acks[i])
      sim_playloc.append(playloc)
      sim_extrabuff.append(extrabuff)
#now we are done playing for the time that the data was being streamed.

  stats['T_rebuf']=sim_realtime[-1]-sim_playloc[-1]
  for i in range(0,len(sim_playloc)-1):
    if sim_playloc[i]>0:
      stats['T_init']=sim_realtime[i]
      break

  sim_playloc_uniq=[]
  sim_realtime_uniq=[]
  for i in range(1,len(sim_playloc)):
    if (sim_realtime[i-1]!=sim_realtime[i] ):
      sim_playloc_uniq.append(sim_playloc[i-1])
      sim_realtime_uniq.append(sim_realtime[i-1])


  playing=False
  for i in range(1,len(sim_playloc_uniq)):
    if (sim_playloc_uniq[i-1]!=sim_playloc_uniq[i] ):
      if (not playing):
        #print "i:",i,"playloc : ",sim_playloc[i-1],"realtime : ",sim_realtime[i-1]
        stats['N_rebuf']+=1
        playing=True
    else:
      #if playing:
        #print "i:",i,"Setting false |playloc : ",sim_playloc[i-1],"realtime : ",sim_realtime[i-1]
      playing=False



#adding data seqence received
  stats['F_rebuf']=1.0*stats['N_rebuf']/totlen
  stats['qoe']=getQoe(-1,stats['T_init'],stats['F_rebuf'],stats['T_rebuf'],stats['vidlen'])
  title="Threshold="+str(threshold)+"secs"
  fig=Figure()
  for i in range(0,len(sim_acks)):
    sim_acks[i]=sim_acks[i]/1000
  ax=fig.add_subplot(111,xlabel="Real Time",ylabel="Ack Number Sent(in KBytes)",title=title,xlim=[min(realtime),max(realtime)],ylim=[min(sim_acks),max(sim_acks)])
  ax.plot(sim_realtime,sim_acks,"g-")

  fig_playloc=Figure()
  ax=fig_playloc.add_subplot(111,xlabel="Real Time",ylabel="Play Location",title=title,xlim=[min(realtime),max(realtime)],ylim=[min(sim_playloc),max(sim_playloc)])
  ax.plot(sim_realtime,sim_playloc,"b-")
  canvas_playloc=FigureCanvas(fig_playloc)
  canvas_playloc.print_figure(os.getcwd()+"/Video_Performance/static/vperf_playloc.png")

  fig_playloc2=Figure()
  ax=fig_playloc2.add_subplot(111,xlabel="Real Time",ylabel="Buffered Data",title=title,xlim=[min(realtime),max(realtime)],ylim=[min(sim_extrabuff),max(sim_extrabuff)])
  ax.plot(sim_realtime,sim_extrabuff,"r^-")
  canvas_playloc2=FigureCanvas(fig_playloc2)
  canvas_playloc2.print_figure(os.getcwd()+"/Video_Performance/static/vperf_extrabuff.png")

  fig_datareqd=Figure()
  ax=fig_datareqd.add_subplot(111,xlabel="Video Time",ylabel="[encoded][unscaled]Data Required to View Video till time t", title=" Video Bit Rate",xlim=[min(vidtime),max(vidtime)],ylim=[min(datareqd),max(datareqd)])
  ax.plot(vidtime,datareqd,"bs-")
  canvas_datareqd=FigureCanvas(fig_datareqd)
  canvas_datareqd.print_figure(os.getcwd()+"/Video_Performance/static/vperf_datareqd.png")

#creating the canvas and sending it out.
  canvas=FigureCanvas(fig)
  response=HttpResponse(content_type='image/png')
  canvas.print_figure(os.getcwd()+"/Video_Performance/static/vperf_acks.png")
  return stats

def bitrate(request):
  traceid=int(request.GET.get('id'))
  sec=float(request.GET.get('sec'))
  rate=float(request.GET.get('rate'))
  bt=models.PlayDataReq()
  bt.tcpConn=models.TcpConn.objects.get(pk=traceid)
  bt.playLoc=sec
  bt.playData=rate
  bt.save()
  return HttpResponse("")

def addphoneconf(request):
  signal_strength=float(request.GET.get('signal_strength'))
  phoneConf=models.PhoneConf()
  phoneConf.signal_strength=signal_strength
  phoneConf.save()
  return HttpResponse(str(phoneConf.pk))

def addqoe(request):
  tinit=float(request.GET.get('tinit'));
  trebuf=float(request.GET.get('trebuf'));
  frebuf=float(request.GET.get('frebuf'));
  qoe=float(request.GET.get('qoe'));
  vidid=str(request.GET.get('url'))
  quality=str(request.GET.get('quality'))
  vidlen=float(request.GET.get('vidlen'))
  phoneConf=int(request.GET.get('phoneConf'))
  qoedata=models.TcpConn()
  qoedata.tinit=tinit
  qoedata.trebuf=trebuf
  qoedata.frebuf=frebuf
  qoedata.qoe=qoe
  qoedata.url=vidid
  qoedata.vidlen=int(vidlen)
  qoedata.quality=quality
  qoedata.src_ip="some ip"
  qoedata.src_port=0
  qoedata.dst_ip="some ip"
  qoedata.dst_port=80
  qoedata.phoneConf=phoneConf
  qoedata.save()
  return HttpResponse(str(qoedata.pk));

def addtcppacket(request):
  tcpConn=float(request.GET.get('tcpConn'));
  timestamp=float(request.GET.get('timestamp'));
  ackno=float(request.GET.get('ackno'));
  pckt=models.TcpPacket()
  pckt.tcpConn=models.TcpConn.objects.get(pk=tcpConn)
  pckt.timestamp=datetime.datetime.fromtimestamp(timestamp)
  pckt.src2dst=True
  pckt.ackno=ackno
  pckt.ack=True
  pckt.seqno=-1
  pckt.window_size=0
  pckt.datalen=-1
  pckt.save()
  return HttpResponse("")

def addstallloc(request):
  tcpConn=float(request.GET.get('tcpConn'));
  timestamp=float(request.GET.get('timestamp'));
  pckt=models.StallLoc()
  pckt.tcpConn=models.TcpConn.objects.get(pk=tcpConn)
  pckt.stallLoc=timestamp
  pckt.save()
  return HttpResponse("")

def addbitrate(request):
  tcpConn=float(request.GET.get('tcpConn'));
  timestamp=float(request.GET.get('timestamp'));
  datareqd=float(request.GET.get('datareqd'))
  pckt=models.PlayDataReq()
  pckt.tcpConn=models.TcpConn.objects.get(pk=tcpConn)
  pckt.playLoc=timestamp
  pckt.playData=datareqd
  pckt.save()
  return HttpResponse("")

def regression(request):
  data0=models.TcpConn.objects.all()
  data=[]
  for test in data0:
    if test.qoe>=0:
      data.append(test)
  #data1={'qoe': [a.qoe for a in data],'tinit': [(a.tinit/1000) for a in data],'trebuf': [a.trebuf/(a.vidlen*1000) for a in data],'frebuf': [a.frebuf*(a.vidlen)/((a.trebuf/1000)+a.vidlen) for a in data]}
  #data1={'qoe': [a.qoe for a in data],'tinit': [(a.tinit/1000)/(a.vidlen+(a.trebuf/1000)) for a in data],'trebuf': [(a.trebuf/1000)/(a.vidlen+(a.trebuf/1000)) for a in data],'frebuf': [a.frebuf for a in data]}
  data1={'qoe': [a.qoe for a in data],'tinit': [(a.tinit)/(a.vidlen) for a in data],'trebuf': [(a.trebuf/1000)/(a.vidlen) for a in data],'frebuf': [a.frebuf-1.0/a.vidlen for a in data],'avgstalltime':[(a.trebuf/1000)/(a.vidlen*a.frebuf) for a in data]}
  qoedata = robjects.FloatVector(data1['qoe'])
  tinitdata=robjects.FloatVector(data1['tinit'])
  trebufdata=robjects.FloatVector(data1['trebuf'])
  frebufdata= robjects.FloatVector(data1['frebuf'])
  avgstalltime= robjects.FloatVector(data1['avgstalltime'])
  robjects.globalEnv['qoe']=qoedata
  robjects.globalEnv['tinit']=tinitdata
  robjects.globalEnv['frebuf']=frebufdata
  robjects.globalEnv['trebuf']=trebufdata
  robjects.globalEnv['avgstalltime']=avgstalltime
  #m=robjects.r.lm("qoe~tinit+frebuf+trebuf")
  m=robjects.r.lm("qoe~frebuf+trebuf+tinit+avgstalltime")
  #factors = ['tinit', 'frebuf', 'trebuf']
  factors = ['frebuf', 'trebuf']
  summary = robjects.r.summary(m)



  def draw_graph_one_var(x):
    reg=r.lm('qoe~%s'%(x))
    coef=None
    try: coef=get_coefficients(reg)
    except ValueError: pass
    r.png(os.getcwd()+"/Video_Performance/static/one_var_%s.png"%(x), 512, 512)
    r.plot(data1[x], data1['qoe'],ylab="qoe", xlab=x)
    if(coef):
      r.abline(a=coef[0], b=coef[1],col='red')
    r['dev.off']()


  for var in factors:
    draw_graph_one_var(var)
  return render_to_response('regression.html', {'together':str(summary), 'individual':factors})

def get_coefficients(reg):
  summary = str(reg[9])
  coef=summary[summary.find("Coefficients:"):].split("\n")
  ws=re.compile(r'\s+')
  return map(float,ws.split(coef[2].strip()))


def parse_summary(summary):
  _summary=summary[summary.find(')\n')+2:]
  op={}
  ws=re.compile(r'\s+')
  lines=_summary.split('\n')
  for line in  lines:
    line_data=ws.split(line);
    op[line_data[0]]=line_data[1:]
  return op;


def updatebitrate(tcpConn):
  conn=models.TcpConn.objects.get(pk=tcpConn)
#delete any present entries about this conn in the bitrate table
  models.PlayDataReq.objects.filter(tcpConn=conn).delete()
#download the video from the video url
  os.system('youtube-dl '+conn.url)
  print "finished download of video"

def getAvgDownloadRate(entry):
    firstpckt=models.TcpPacket.objects.all().filter(tcpConn=entry).order_by('timestamp')[:1][0] #get all packets for the trace in the order they were received
    lastpckt=(models.TcpPacket.objects.all().filter(tcpConn=entry).order_by('timestamp').reverse()[:1])[0] #get all packets for the trace in the order they were received
    #print entry.id
    return (lastpckt.ackno-firstpckt.ackno)/((lastpckt.timestamp- firstpckt.timestamp).seconds*1000)

def getBitrate(entry):
    firstpckt=models.TcpPacket.objects.all().filter(tcpConn=entry).order_by('timestamp')[:1][0] #get all packets for the trace in the order they were received
    lastpckt=(models.TcpPacket.objects.all().filter(tcpConn=entry).order_by('timestamp').reverse()[:1])[0] #get all packets for the trace in the order they were received
    return (lastpckt.ackno-firstpckt.ackno)/entry.vidlen

def cleanupEntriesFromCache():
  cons=models.TcpConn.objects.all()
  for conn in cons:
    pkts=models.TcpPacket.objects.all().filter(tcpConn=conn).order_by('timestamp') #get all packets for the trace in the order they were received
    if conn.vidlen>len(pkts) and getAvgDownloadRate(conn)>200:
      print conn.id, ": ", conn.vidlen, len(pkts), getAvgDownloadRate(conn)

#all times are in seconds
def getQoe(qoe,tinit,frebuf,trebuf,vidlen):
  if qoe>0:
    return qoe
  #return  5.007 - (6.34*0.001*tinit)-(3.653*frebuf)-(3.916*0.001*trebuf)
  time=vidlen+trebuf
  #return  4.72 + (1.13*tinit/vidlen)-(5.131*frebuf)-(0.191*trebuf/vidlen)
  return  4.72  -(5.131*frebuf)-(0.191*trebuf/vidlen)

def getTime(entry):
  pckts= (models.TcpPacket.objects.all().filter(tcpConn=entry)[:1])
  for pckt in pckts:
    return pckt.timestamp.hour
def getTimePercentageInStalling(entry):
  return (((entry.trebuf/1000)-(entry.vidlen))/((entry.trebuf/1000)))*100 #since trebuf is in mili
#will analyse the graph over variation on time of day here!
def timeofday(checkspeedlimit,quality):
  entries=models.TcpConn.objects.all().order_by('id').filter(quality=quality)
  #entries=models.TcpConn.objects.all().order_by('id').reverse()






  stallperc_time=[]
  stallperc_reading=[]
  dwnldrate_time=[]
  dwnldrate_reading=[]
  qoe_time=[]
  qoe_max_reading=[]
  qoe_min_reading=[]
  qoe_tot_reading=[]
  obs_time=[]
  obs_reading=[]


  for time in range(0,24):
    count=0
    rate=0
    qoe_max=0
    qoe_min=5
    qoe_tot=0
    timespent=0
    obs=0
    #print "Time :",time
    for entry in entries:
      if getTime(entry)==time:
        dwndrate=getAvgDownloadRate(entry)
        #print "id:",entry.id,"Time Of Entry:", time,"Avg download rate:",dwndrate,"Condn:",((checkspeedlimit and (dwndrate<50)) or (not(checkspeedlimit) and (dwndrate>50)))
        if ((checkspeedlimit and (dwndrate<35)) or (not(checkspeedlimit) and (dwndrate>35))):
          count=count+1
          rate = rate+ dwndrate
          qoe_min=min(qoe_min,getQoe(entry.qoe,entry.tinit/1000,entry.frebuf,entry.trebuf/1000,entry.vidlen))
          qoe_max=max(qoe_max,getQoe(entry.qoe,entry.tinit/1000,entry.frebuf,entry.trebuf/1000,entry.vidlen))
          qoe_tot=qoe_tot+getQoe(entry.qoe,entry.tinit/1000,entry.frebuf,entry.trebuf/1000,entry.vidlen)
          timespent=timespent+getTimePercentageInStalling(entry)
          obs=obs+1
    if count>0:
      dwnldrate_reading.append(rate/count)
      qoe_tot_reading.append(qoe_tot/count)
      qoe_max_reading.append(qoe_max)
      qoe_min_reading.append(qoe_min)
      stallperc_reading.append(timespent/count)
    else:
      dwnldrate_reading.append(0)
      qoe_tot_reading.append(0)
      qoe_max_reading.append(0)
      qoe_min_reading.append(0)
      stallperc_reading.append(0)

    qoe_time.append(time)
    stallperc_time.append(time)
    dwnldrate_time.append(time)
    obs_time.append(time)
    obs_reading.append(obs)


  s="";
  mydict={}
  mydict['stallperc_time']=stallperc_time
  mydict['stallperc_reading']=stallperc_reading
  mydict['dwnldrate_time']=dwnldrate_time
  mydict['dwnldrate_reading']=dwnldrate_reading
  mydict['qoe_time']=qoe_time
  mydict['qoe_max_reading']=qoe_max_reading
  mydict['qoe_min_reading']=qoe_min_reading
  mydict['qoe_tot_reading']=qoe_tot_reading
  mydict['obs_time']=obs_time
  mydict['obs_reading']=obs_reading
  connectiontype ="2G" if checkspeedlimit else  "3G"
  s+="figure('visible','off')\n"
  s+="x= %s\n"%(str(stallperc_time))
  s+="stallperc_reading_"+quality+"_"+str(connectiontype)+"= %s\n"%(str(stallperc_reading))
  s+="dwnldrate_reading_"+quality+"_"+str(connectiontype)+"= %s\n"%(str(map(float, dwnldrate_reading)))
  s+="qoe_reading_"+quality+"_"+str(connectiontype)+"= %s\n"%(str(qoe_tot_reading))
  s+="obs_reading_"+quality+"_"+str(connectiontype)+"= %s\n"%(str(obs_reading))
  s+="f1=figure();b1=bar(x,stallperc_reading)\n"
  s+="f2=figure();b2=bar(x,dwnldrate_reading)\n"
  s+="f3=figure();b3=bar(x,qoe_reading)\n"
  s+="f4=figure();b4=bar(x,obs_reading)\n"
  s+="set(findall(f1,'type','axes'),'XTick',x)\n"
  s+="set(findall(f2,'type','axes'),'XTick',x)\n"
  s+="set(findall(f3,'type','axes'),'XTick',x)\n"
  s+="set(findall(f4,'type','axes'),'XTick',x)\n"
  s+="xlabel(findall(f1,'type','axes'),'Time of the Day')\n"
  s+="xlabel(findall(f2,'type','axes'),'Time of the Day')\n"
  s+="xlabel(findall(f3,'type','axes'),'Time of the Day')\n"
  s+="xlabel(findall(f4,'type','axes'),'Time of the Day')\n"
  s+="ylabel(findall(f1,'type','axes'),'Percentage of Time in Rebuffering State')\n"
  s+="ylabel(findall(f2,'type','axes'),'Average Download Rate')\n"
  s+="ylabel(findall(f3,'type','axes'),'Average Quality of Experience')\n"
  s+="ylabel(findall(f4,'type','axes'),'Number of Readings')\n"
  s+="set(gca,'XLim',[-1 24])\n"
  s+="saveas(f1,'f1_"+quality+"_"+str(connectiontype)+".jpg')\n"
  s+="saveas(f2,'f2_"+quality+"_"+str(connectiontype)+".jpg')\n"
  s+="saveas(f3,'f3_"+quality+"_"+str(connectiontype)+".jpg')\n"
  s+="saveas(f4,'f4_"+quality+"_"+str(connectiontype)+".jpg')\n"
  s+="close(f1)\n"
  s+="close(f2)\n"
  s+="close(f3)\n"
  s+="close(f4)\n"
  print s;
  return render_to_response('timeofday.html',mydict)

def timeofday2g(request):
  return timeofday(True,request.GET.get('quality'))

def timeofday3g(request):
  return timeofday(False,request.GET.get('quality'))

def VideoSpecificAnalysis(checkspeedlimit):
  mydict={}
  return render_to_response('videospecificanalysis.html',mydict)

def videostats2g(request):
  return VideoSpecificAnalysis(True)

def videostats3g(request):
  return VideoSpecificAnalysis(False)

def cdfanalysis(checkspeedlimit):
  entries0=models.TcpConn.objects.all().order_by('id').filter()
  entries=[]

  for entry in entries0:
    dwndrate=getAvgDownloadRate(entry)
    if ((checkspeedlimit and (dwndrate<35)) or (not(checkspeedlimit) and (dwndrate>35))):
      entries.append(entry)

  time_buckets=[]
  for i in range(0,24):
    time_buckets.append([])

  for entry in entries:
    time_buckets[getTime(entry)].append(entry)

  response="<html><body>"
  t=0
  samples_cdf={}
  samples_dwnldrate={}
  for bucket in time_buckets:
    ratesamples=[]
    cdf=[]
    for entry in bucket:
      ratesamples.append(getAvgDownloadRate(entry))

    ratesamples.sort()
    count=0
    for i in ratesamples:
      count+=1.0/len(ratesamples)
      cdf.append(count)

    if len(ratesamples)>0:
      fig_playloc=Figure()
      ax=fig_playloc.add_subplot(111,xlabel="download rate",ylabel="cdf",title="cdf at time="+str(t),xlim=[min(ratesamples),max(ratesamples)],ylim=[min(cdf),max(cdf)])
      ax.plot(ratesamples,cdf,"bs-")
      canvas_playloc=FigureCanvas(fig_playloc)
      canvas_playloc.print_figure(os.getcwd()+"/Video_Performance/static/vperf_cdf"+str(t)+".png")
      response+="<img src=\"/static/vperf_cdf"+str(t)+".png\"/>"
      samples_cdf[str(t)]=cdf
      samples_dwnldrate[str(t)]=ratesamples


      rates=[50,60,70,80,90,100,110,120,130,140,150,160]
      response+="<table border=\"1\">"
      for rate in rates:
        response+="<tr>\n"
        response+="<td>"+str(rate)+"</td>"
        j=0
        for sample in ratesamples:
          setj=True
          if sample<rate:
            setj=False
          if not(setj):
            j+=1
        print j,len(ratesamples)
        try:
          if(j-1)>=0:
            end=0
          response+="<td>"+"("+str(j)+")"+str(1-(cdf[j]+1.0*(ratesamples[j]-rate)/(len(ratesamples)*(ratesamples[j]-end))))+"</td>"

        except Exception as e:
          print e
        response+="</tr>\n"

    t+=1

    response+="</table>"

  fig_cdfanal=Figure()
  ax=fig_cdfanal.add_subplot(111,xlabel="Cumulative Probability",ylabel="Download Speed(KBytes/s)",title="Variation in Download Speed with Time")
  ax.plot(samples_cdf['3'],samples_dwnldrate['3'],"b-",label="3:00 am")
  ax.plot(samples_cdf['7'],samples_dwnldrate['7'],"y-",label="7:00 am")
  ax.plot(samples_cdf['10'],samples_dwnldrate['10'],"r-",label="10:00 am")
  ax.plot(samples_cdf['13'],samples_dwnldrate['13'],"g-",label="13:00 pm")
  handles,labels=ax.get_legend_handles_labels()
  ax.legend(handles,labels)
  canvas_cdfanal=FigureCanvas(fig_cdfanal)
  canvas_cdfanal.print_figure(os.getcwd()+"/Video_Performance/static/vperf_cdfanal.png")

  response+="<img src=\"/static/vperf_cdfanal.png\"/>"



  response+="</body></html>"
  return HttpResponse(response)



def cdf2g(request):
  return cdfanalysis(True)

def cdf3g(request):
  return cdfanalysis(False)

#def datareqd(request):
  #conn=models.TcpConn.objects.get(pk=18)
  #ratesamples=models.PlayDataReq.objects.all().filter(tcpConn=conn) #get all buffrate for the trace in the order they were received
  #vidtime=[]
  #datareqd=[]
  #for smpl in ratesamples:
    #vidtime.append(smpl.playLoc)
    #datareqd.append(smpl.playData)

  #fig_datareqd=Figure()
  #ax=fig_datareqd.add_subplot(111,xlabel="Video Time",ylabel="[encoded][unscaled]Data Required to View Video till time t", title=" Video Bit Rate",xlim=[min(vidtime),max(vidtime)],ylim=[min(datareqd),max(datareqd)])
  #ax.plot(vidtime,datareqd,"bs-")
  #canvas_datareqd=FigureCanvas(fig_datareqd)
  #canvas_datareqd.print_figure(os.getcwd()+"/Video_Performance/static/vperf_datareqd.png")
  #return HttpResponse("hjkasdhdk")

def summary(request):
  entries=models.TcpConn.objects.all().order_by('id')
  dataentries=[]
  for entry in entries:
    if getAvgDownloadRate(entry)>00 and entry.quality=='medium':
      tempdict={}
      tempdict['id']=entry.id
      tempdict['quality']=entry.quality
      tempdict['vidlen']=entry.vidlen
      tempdict['tinit']=entry.tinit
      tempdict['frebuf']=entry.frebuf
      tempdict['trebuf']=entry.trebuf
      tempdict['qoe']=getQoe(entry.qoe,entry.tinit/1000,entry.frebuf,entry.trebuf/1000,entry.vidlen)
      tempdict['dwndrate']=getAvgDownloadRate(entry)
      tempdict['hour']=getTime(entry)
      tempdict['perctime']=getTimePercentageInStalling(entry)
      tempdict['bitrate']=getBitrate(entry)
      dataentries.append(tempdict)
  avgdwnldrate={}
  mindwnldrate={}
  maxdwnldrate={}
  count={}
  for i in range(0,24):
    avgdwnldrate[i]=0
    mindwnldrate[i]=500000
    maxdwnldrate[i]=0
    count[i]=0
  for entry in dataentries:
    mindwnldrate[entry['hour']]=min(mindwnldrate[entry['hour']],entry['dwndrate'])
    maxdwnldrate[entry['hour']]=max(mindwnldrate[entry['hour']],entry['dwndrate'])
    temp=avgdwnldrate[entry['hour']]*count[entry['hour']]
    count[entry['hour']]=count[entry['hour']]+1
    avgdwnldrate[entry['hour']]=(temp+entry['dwndrate'])/count[entry['hour']]

  mydict={}
  mydict['dataentries']=dataentries
  mydict['sample']=dataentries[0]
  mydict['mindwnldrate']=mindwnldrate
  mydict['maxdwnldrate']=maxdwnldrate
  mydict['avgdwnldrate']=avgdwnldrate
  return render_to_response('vperf_summary.html',mydict)

def correctTimestamp():
  entries=models.TcpConn.objects.all().order_by('id')
  for entry in entries:
    if getAvgDownloadRate(entry)<30 and entry.id>288:
      pkts=models.TcpPacket.objects.all().filter(tcpConn=entry)
      print "id: ",entry.id,"time: ", pkts[0].timestamp, "avg rate: ",getAvgDownloadRate(entry)
      #if raw_input("Do you want to correct this entry(y/n)?").lower() in ['y', 'yes' ]:
      if True:
        for pkt in pkts:
          dt=datetime.timedelta(hours=10, minutes=30) # diff b/w india and us timestamps
          newtimestamp=pkt.timestamp-dt
          print pkt.timestamp,  newtimestamp
          pkt.timestamp=newtimestamp
          pkt.save()

def arbit():
  entries=models.TcpConn.objects.all().order_by('id')
  for entry in entries:
    if getTime(entry) in [12,13,14]:
      print entry.id,  getAvgDownloadRate(entry) , entry.quality, getTime(entry)
