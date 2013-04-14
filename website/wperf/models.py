
from django.db import models
# Create your models here.


class Tester(models.Model):
    deviceId = models.CharField(max_length=100)


class Resource(models.Model):
    url = models.CharField(max_length=1000)


class Test(models.Model):
    tester = models.CharField(max_length=100)
    gsmCellId = models.BigIntegerField(default=0)
    operator = models.CharField(max_length="50")
    networkType = models.IntegerField()  # whether GPRS or EDGE or what!
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)


class Website(models.Model):
    testId = models.ForeignKey(Test)
    timestamp = models.DateTimeField(auto_now_add=True)
    url = models.CharField(max_length=1000)
    dnsTime = models.BigIntegerField(default=0)
    pageLoadTime = models.BigIntegerField(default=0)
    javascriptTime = models.BigIntegerField(default=0)
    pageTotalSize = models.IntegerField(default=0)
    rating = models.FloatField(default=0)
    progressTimeMap = models.CharField(max_length=1000)
    #gsmLocationAreaCode=models.BigIntegerField(default=0)


    #country can be easily be inferred from operator field
    #since operator field is in the form MCC+MNC
    #MCC=mobile country code
    #MNC=mobile network code


class WebSiteResource(models.Model):
    resourceId = models.ForeignKey(Resource)
    websiteId = models.ForeignKey(Website)


class UploadedFile(models.Model):
    filetype = models.CharField(max_length=20)
    uploadedfile = models.FileField(upload_to="%Y/%m/%d")
    shortfilename = models.CharField(max_length=100)
    processed = models.BooleanField(default=False)


class PcapFile(models.Model):
    uploadedfile = models.FileField(upload_to="%Y/%m/%d")
    shortfilename = models.CharField(max_length=100)
    uploadLimit = models.FloatField(default=132.0/8)
    downloadLimit = models.FloatField(default=1085.0/8)


class Organization(models.Model):
    name = models.CharField(max_length=1000)
    ip_range = models.CharField(max_length=500)
    lower = models.BigIntegerField()
    higher = models.BigIntegerField()


class StreamType(models.Model):
    class Options:
        ADS = "Ads"
        MAIN = "Main"
        UNKNOWN = "Unknown"
    name = models.CharField(max_length=100, default=Options.UNKNOWN)


class Host(models.Model):
    name = models.CharField(max_length=100)
    blocked = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)
    org = models.ForeignKey(Organization)
    stream_type = models.ForeignKey(StreamType, null=True, blank=True)


class IP(models.Model):
    ip = models.CharField(max_length = 100)


class HostIp(models.Model):
    hostId = models.ForeignKey(Host)
    ip = models.CharField(max_length=100)


class HostPcap(models.Model):
    hostId = models.ForeignKey(Host)
    pcapId = models.ForeignKey(PcapFile)


