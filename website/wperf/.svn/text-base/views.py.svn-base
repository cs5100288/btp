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
    print request.raw_post_data
    obs=models.Observation.objects.get(pk=pk)
    obs.url=request.POST['url']
    obs.rating=request.POST['rating']
    obs.save()
    return HttpResponse("")

@csrf_exempt
def getnewobsid(request):
  if request.method=='POST':
    w=models.Observation()
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
      newfile=models.UploadedFile(filetype="None",uploadedfile=request.FILES['uploadfile'])
      newfile.save()
      return HttpResponseRedirect(reverse(listfiles))
  else:
    form=forms.UploadForm()
    return render_to_response(
        'list.html',
        {'uploadedfiles':[],'form':form},
        context_instance=RequestContext(request)
        )

