
from django.db import models
# Create your models here.

class Tester(models.Model):
  deviceId=models.CharField(max_length=100)

class Resource(models.Model):
  url=models.CharField(max_length=1000)

class Observation(models.Model):
  timestamp=models.DateTimeField(auto_now_add=True)
  url=models.CharField(max_length=1000)
  tester=models.CharField(max_length=100)
  dnsTime=models.BigIntegerField(default=0)
  pageLoadTime=models.BigIntegerField(default=0)
  javascriptTime=models.BigIntegerField(default=0)
  pageTotalSize=models.IntegerField(default=0)
  gsmCellId=models.BigIntegerField(default=0)
  #gsmLocationAreaCode=models.BigIntegerField(default=0)


  #country can be easily be inferred from operator field
  #since operator field is in the form MCC+MNC
  #MCC=mobile country code
  #MNC=mobile network code
  operator=models.CharField(max_length="50")
  latitude=models.FloatField(default=0)
  longitude=models.FloatField(default=0)
  rating=models.FloatField(default=0)
  networkType=models.IntegerField() #whether GPRS or EDGE or what!

class WebSiteResource(models.Model):
  resourceId=models.ForeignKey(Resource)
  websiteId=models.ForeignKey(Observation)


class Test(models.Model):
  name=models.CharField(max_length=100)
  comments=models.CharField(max_length=1000)

class TestInstance(models.Model):
  Test=models.ForeignKey(Test)

#class TestObs(models.Model):
  #TestInstance=models.ForeignKey(TestInstance)
  #Observation=models.ForeignKey(Observation)

class UploadedFile(models.Model):
  filetype=models.CharField(max_length=20)
  uploadedfile=models.FileField(upload_to="%Y/%m/%d")
