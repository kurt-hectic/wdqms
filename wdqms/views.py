from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from .models import Period

from datetime import date,timedelta,datetime

def index(request):
    template = loader.get_template('index.html')
    context = {}
    return HttpResponse(template.render(context,request))

def map(request):
    style = request.GET.get('style','wdqmsmap')
    if style not in ['wdqmsmap','wdqmsmaplpr']:
      raise ValueError("{} not supported".format(style))
    template = loader.get_template('map.html')
    context = {'style':style}

    return HttpResponse(template.render(context,request))

def listimports_json(request):

    mytype = request.GET.get('type','')
    center = request.GET.get('center','')

    if mytype not in ["SYNOP","TEMP"] or center not in ["ECMWF","JMA","DWD","NCEP"]:
      raise ValueError("unsupported argument")

    periods = Period.objects.filter(center=center,filetype=mytype)
    mindate = periods.first().to_date().strftime("%Y/%m/%d")
    maxdate = periods.last().to_date().strftime("%Y/%m/%d")

    dates = {}
    for period in periods:
       key = period.to_date().strftime("%Y/%m/%d")
       if key in dates:
         dates[key].append(str(period.hour))
       else:
         dates[key] = [str(period.hour),]

    data = { 'dates' : dates , 'mindate' : mindate, 'maxdate' : maxdate, 'maxtime' : dates[maxdate][-1], 'maxtimes' : dates[maxdate] }

    return JsonResponse(data)

def listimports(request):
    now = datetime.now()
    periods = Period.objects.all()
    period_idx = {}
    for p in periods:
       period_idx[str(p)]=True

    startdate = date(2016,1,1)
    enddate = date.today()
    delta = enddate - startdate
    dates  = []
    for i in range(delta.days + 1):
         dates.append(startdate + timedelta(days=i))

    centers = ["ECMWF","JMA","DWD","NCEP"] 
    tempcenters = ["ECMWF","JMA"]

    template = loader.get_template('listimports.html')
    context = {'now': now , 'periods' : period_idx , 'dates' : list(reversed(dates)), 
	'centers' : centers , 'tempcenters' : tempcenters , 'nwpperiods' : range(0,24,6), 'tempstartdate' : date(2017,1,1) }

    return HttpResponse(template.render(context,request))
    
