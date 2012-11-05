from django.db import models

# Create your models here.

class PhoneConf(models.Model):
  signal_strength=models.FloatField();
  timeofday = models.DateTimeField(auto_now_add=True)
class TcpConn(models.Model):
  src_ip=models.CharField(max_length=17) #supports ipv6 too
  dst_ip=models.CharField(max_length=17)
  src_port=models.IntegerField()
  dst_port=models.IntegerField()
  url=models.CharField(max_length=200)
  comments=models.CharField(max_length=200)
  quality=models.CharField(max_length=10)
  vidlen=models.IntegerField() #length of a video in seconds
  tinit=models.FloatField();
  frebuf=models.FloatField();
  trebuf=models.FloatField();
  qoe=models.FloatField();
  phoneConf=models.ForeignKey(PhoneConf)


class TcpPacket(models.Model):
  tcpConn=models.ForeignKey(TcpConn)
  src2dst=models.BooleanField() #if true the packet is going from source to destination, else is being received by dest
  timestamp=models.DateTimeField()
  seqno=models.BigIntegerField()
  ackno=models.BigIntegerField()
  window_size=models.BigIntegerField()
  urg=models.BooleanField() #TH_URG: Urgent.
  ack=models.BooleanField() #TH_ACK: Acknowledgement.
  push=models.BooleanField() #TH_PUSH: Push.
  rst=models.BooleanField() #TH_RST: Reset.
  syn=models.BooleanField() #TH_SYN: Synchronization.
  fin=models.BooleanField() #TH_FIN: Final.
  datalen=models.IntegerField() #length of the data in the  tcp packet

class PlayDataReq(models.Model):
  tcpConn=models.ForeignKey(TcpConn) #the id of the tcp connection in question
  playLoc=models.FloatField() #the seconds at which we are concerned
  playData=models.FloatField() #bitrate at that second

class StallLoc(models.Model):
  tcpConn=models.ForeignKey(TcpConn) #the id of the tcp connection in question
  stallLoc=models.FloatField() #the seconds at which Video stalled

class Counter(models.Model):
  val=models.IntegerField();
  comments=models.CharField(max_length=100)
