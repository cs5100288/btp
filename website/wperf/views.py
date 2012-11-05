# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from django.template import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import *
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import models,forms
import random
from django.core.urlresolvers import reverse
import subprocess
import urllib,urllib2
import re


def homepage(request):
  mydict={}
  return render_to_response('wperf_index.html',mydict)

def nextsite(request):
  last=models.Website.objects.count()-1
  rand_index=random.randint(0,last)
  chosenOne=models.Website.objects.all()[rand_index]
  return HttpResponse(chosenOne.address)

@csrf_exempt
def addobservation(request,pk):
  if request.method=='POST':
    datas=request.POST['data']
    data=eval(datas)
    for key in data.keys():
      w=models.Website()
      w.testId=models.Test.objects.get(pk=int(pk))
      w.url=key
      w.pageLoadTime=data[key]['pageLoadTime']
      w.rating=data[key]['rating']
      w.progressTimeMap=data[key]['progressTimeMap']
      w.save()
    return HttpResponse("")

@csrf_exempt
def getnewobsid(request):
  if request.method=='POST':
    w=models.Test()
    w.tester=request.POST['tester']
    w.gsmCellId=request.POST['gsmCellId']
    w.operator=request.POST['operator']
    w.networkType=request.POST['networkType']
    w.save()
    return HttpResponse("id:"+str(w.pk))

def test(request):
  mydict={}
  return render_to_response('test.html', mydict)
def listfiles(request):
  form=forms.UploadForm()
  return render_to_response(
        'list.html',
        {'uploadedfiles':models.UploadedFile.objects.all(),'form':form},
        context_instance=RequestContext(request)
        )

def upload(request):
  if request.method=='POST':
    form=forms.UploadForm(request.POST,request.FILES)
    if form.is_valid():
      newfile=models.UploadedFile(filetype="None",uploadedfile=request.FILES['uploadfile'], shortfilename=request.FILES['uploadfile'].name ,processed=False)
      newfile.save()
      s= newfile.uploadedfile.name
      s=s[s.rfind('/')+1:]
      newfile.shortfilename=s
      newfile.save()
      return HttpResponseRedirect(reverse(listfiles))
  else:
    form=forms.UploadForm()
    return render_to_response(
        'list.html',
        {'uploadedfiles':[],'form':form},
        context_instance=RequestContext(request)
        )

def get_location_from_hostip_info(ip=""):
  url = 'http://api.hostip.info/get_html.php?position=true'
  if len(ip) >0:
    url = url+'&ip='+str(ip)
  response=urllib.urlopen(url).read()
  return response

def map_traceroute(request,ip):
  # p = subprocess.Popen(['traceroute', ip], stdout=subprocess.PIPE)
  # p.wait()
  # output=p.communicate()
  output = "Beginning Traceroute to "+str(ip)+"..."  
  mydict={}
  mydict['output']=output
  # ips=[]
  # locs=[]
  # ips.append('')
  # for line in output.split('\n')[1:]:
  #   m=re.match(r'.*?\((.*?)\).*',line)
  #   if m:
  #     ips.append(m.group(1))
  # for ip in ips:
  #   l = get_location_from_hostip_info(ip)

  return render_to_response('maps.html',mydict)