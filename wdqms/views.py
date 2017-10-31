from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from .models import Period,Country,Station
from django.db.models import Max,Min,Sum,Count
from datetime import date,timedelta,datetime
from django.db import connection, transaction
from wdqms.decorators import json_response

def index(request):
    template = loader.get_template('index.html')
    context = {}
    return HttpResponse(template.render(context,request))


def listspace(request):

    tables = ['nwpdata','nwpdatabyperiod','emptybyperiod'] 
    cursor = connection.cursor()

    tableinfo = {}
    for table in tables:

        sql = """select total_bytes ,round(extract(epoch from createdate::timestamptz::timestamp::timestamptz)) * 1000 as createdatesecs from dbstats 
		where table_name = '{}' order by createdatesecs""".format(table)
        ret = []
        min = 0

        cursor.execute(sql)
        for row in cursor:
           ret.append([row[0],row[1]])
           if row[0] < min or not min:
              min = row[0]


        tableinfo[table] = { 'min' : min , 'ret' : ret }


    template = loader.get_template('listspace.html')

    context = { 'ret' : ret , 'min' : min , 'tableinfo' : tableinfo }

    return HttpResponse(template.render(context,request))
    

@json_response
def data(request):
    stationindexnbr = request.GET.get('indexnbr')
    center = request.GET.get('center')
    callback = request.GET.get('callback')

    station = Station.objects.filter(indexnbr=stationindexnbr).order_by('-created')[0]

    stationinfo = { 'stationname' : station.name , 'indexnbr' : station.indexnbr, 'countryarea' : station.area , 'countrycode' : station.code,
			'latitude' : station.latitude , 'longitude' : station.longitude }

    sql = """ select i.yyyy,i.mm,i.dd,wigosid,nr_received,nr_expected,nr_rejected,nr_blacklisted,(4-i.cnt) as missing from (
select wigosid,nr_received,nr_expected,nr_rejected,nr_blacklisted,yyyy,mm,dd from vola v join (
select yyyy,mm,dd, invola, vola_id, center, indexnbr, avg(per_used) as per_used , avg(per_received) as per_received,
sum(nr_received) as nr_received,
sum( CASE WHEN hasduplicate THEN 0 ELSE nr_expected END )  as nr_expected,
sum(nr_used) as nr_used, sum(nr_rejected) as nr_rejected,
sum(nr_blacklisted) as nr_blacklisted, sum(nr_passive) as nr_passive, sum(nr_missing) nr_misssing
from stationsbyperiod s where varid in (110,1) group by yyyy,mm,dd,center,indexnbr, vola_id, invola ) ss on v.id=ss.vola_id
where ss.indexnbr=%s and center=%s  ) as ss join ( select yyyy,mm,dd, count(hourperiod) as cnt from imports where center=%s group by yyyy,mm,dd  )  as i on ( ss.yyyy=i.yyyy and ss.mm=i.mm and ss.dd=i.dd ) order by i.yyyy,i.mm,i.dd """


    cursor = connection.cursor()
    cursor.execute(sql,[station.indexnbr,center,center])

    wigosid=None
    data='Day,Nr.Rec,Nr.Exp,Nr.Rej,Nr.Bla,imports missing\n'
    for row in cursor:
        wigosid=row[0]
        day="{}/{}/{}".format(row[0],row[1],row[2])
        data = data+'{},{},{},{},{},{}\n'.format(day,row[4],row[5],row[6],row[7],row[8])

    
    stationinfo["data"] = data
    stationinfo["wigosid"] = wigosid
    stationinfo["indexnbr"] = stationindexnbr

    return stationinfo


def country_dt(request):

    year = request.GET.get('year')
    month = request.GET.get('month')
    day = request.GET.get('day')
    center = request.GET.get('center')
    country_code = request.GET.get('countrycode')
    mytype = request.GET.get('type')

    if not year or not month or not day or not center or not country_code or not mytype :
       raise ValueError("argument error")
        

    norep = "0.001"
    underperf = "0.80"

    if mytype == 'noreport':
       filter="per_received < {} ".format(norep)
    elif mytype == "underperf":
       filter="per_received < {} and per_received >= {} ".format(underperf,norep)
    elif mytype == "quality":
       filter="1>2"
    elif mytype == "normal":
       filter="per_received >= {}".format(underperf)
    else:
       raise ValueError("type {} does not exist".format(mytype))

    sql = """ select nr_expected, nr_received, nr_rejected, nr_blacklisted, ss.indexnbr, v.stationname, v.isocc, v.indexsubnbr, 
			ss.yyyy, ss.mm, ss.dd, ss.center from vola v join (
		select yyyy,mm,dd, invola, vola_id, center, indexnbr, avg(per_used) as per_used , avg(per_received) as per_received,
			sum(nr_received) as nr_received,
			sum( CASE WHEN hasduplicate THEN 0 ELSE nr_expected END )  as nr_expected,
			sum(nr_used) as nr_used, sum(nr_rejected) as nr_rejected,
			sum(nr_blacklisted) as nr_blacklisted, sum(nr_passive) as nr_passive, sum(nr_missing) nr_misssing
			from stationsbyperiod s where varid in (110,1) group by yyyy,mm,dd,center,indexnbr, vola_id, invola ) ss 
	on (v.id=ss.vola_id) 
	where yyyy=%s and mm=%s and dd=%s and center=%s and isocc=%s and {} """.format(filter)

    cursor = connection.cursor()
    cursor.execute(sql,[year,month,day,center,country_code])

    stations = []

    for row in cursor:
        nr_ex = row[0]
        nr_rec = row[1]
        nr_rej = row[2]
        nr_bla = row[3]
        indexnbr = row[4]
        stationname = row[5]
        isocc = row[6]
        indexsubnbr  = row[7]

        myindex = "{}-{}".format(indexnbr,indexsubnbr)

        station = { 'name' : stationname , 'indexnbr' : myindex , 'nrexp' : nr_ex, 'nrrec' : nr_rec, 'nrrej' : nr_rej , 'nrbla' : nr_bla , 'indexnbr2' : indexnbr }
        stations.append(station)



    return JsonResponse( {'data' : stations } )

def country_cal(request):
    max = Period.objects.filter(center='ECMWF',filetype='SYNOP').values_list('date').order_by('date')\
          .annotate(count_periods=Count('hour')).filter(count_periods=4).aggregate(Max('date'))
    min = Period.objects.filter(center='ECMWF',filetype='SYNOP').values_list('date').order_by('date')\
          .annotate(count_periods=Count('hour')).filter(count_periods=4).aggregate(Min('date'))

    incomplete_dates = Period.objects.filter(center='ECMWF',filetype='SYNOP').values_list('date').order_by('date')\
          .annotate(count_periods=Count('hour')).filter(count_periods__lt=4)

    def adjust_date(date):
       return date.strftime('%Y/%m/%d')

    nodates = []
    for idt in incomplete_dates:
        nodates.append(adjust_date(idt[0]))

    return JsonResponse( { 'nodata' : nodates , 'max' : adjust_date(max["date__max"]) , 'min' : adjust_date(min["date__min"])} )
    

def country(request):

    country_code = request.GET.get('cc','UGA')
    country = Country.objects.filter(code=country_code).exclude(vola_code=None)[0]
    if not country:
       raise ValueError("Country with code: {} not enabled".format(country_code))

    countries = Country.objects.all().exclude(vola_code=None)

    yesterday = datetime.now() - timedelta(days=1)
    tabs = [ "noreport" , "underperf" , "quality" , "normal"]


    template = loader.get_template('country.html')
    context = {'country':country, 'countries' : countries, 'yesterday':yesterday , 'tabs' : tabs}
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
    
