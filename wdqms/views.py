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
from django.http import StreamingHttpResponse

import csv
import re
import datetime

def index(request):
    template = loader.get_template('index.html')
    context = {}
    return HttpResponse(template.render(context,request))


def station(request,stationid):
    template = loader.get_template('station.html')

    station = Station.objects.filter(wigosid=stationid).order_by('-created')[0]
    context = {'station' : station }
    return HttpResponse(template.render(context,request))

@json_response 
def nrreceived(request,stationid,variable):

    daysback = int(request.GET.get('daysback',7))

    datefrom = datetime.datetime.strptime(request.GET.get('from','20160101'),'%Y%m%d')
    dateto = datetime.datetime.strptime(request.GET.get('to',(datetime.datetime.now() - datetime.timedelta(1)).strftime('%Y%m%d')),'%Y%m%d')
    encoding = request.GET.get('encoding','json')
    if encoding not in ('csv','json'):
          raise ValueError('no such encoding')

    station = Station.objects.filter(wigosid=stationid).order_by('-created')[0]

    params = { 'wigosid' : stationid , 'variable' : variable , 'from' : datefrom , 'to' : dateto , 'idx' : station.indexnbr }

    sql = """ select s.*,i.nr from 
	(select yyyy,mm,dd,center, sum(nr_received) as rec, sum(nr_expected) as exp from stationsbyperiod where indexnbr = %(idx)s 
		and varid = %(variable)s and assimilationdate between %(from)s and %(to)s  group by center,yyyy,mm,dd ) as s
	join
	( 
	select yyyy,mm,dd,center, count(*) as nr from imports 
	where filetype = 'SYNOP'
	group by yyyy,mm,dd,center
	
	) as i
	on (s.yyyy=i.yyyy and s.mm=i.mm and s.dd=i.dd and s.center = i.center)
	where i.nr = 4
	order by s.center,s.yyyy,s.mm,s.dd """

    with connection.cursor() as cursor:
       cursor.execute(sql, params )

       data = cursor.fetchall()
       if not data:
          raise ValueError('no such station')

       dates = {}
       for d in data:
          mydate = "{}".format(datetime.date(d[0],d[1],d[2]))
          if mydate not in dates:
             dates[mydate]={}
          dates[mydate]["{}-rec".format(d[3])] = d[4]
          dates[mydate]["{}-exp".format(d[3])] = d[5]
 
       if encoding=='json':
          ret = { 'wigosid' : stationid , 'dates' : dates}
       if encoding=='csv':
          data='Day,Expected,ECMWF,JMA,NCEP,DWD\n'
          for mydate,d in sorted(dates.items()):
             ecmwf = d["ECMWF-rec"] if "ECMWF-rec" in d else ''
             dwd = d["DWD-rec"] if "DWD-rec" in d else '' 
             jma = d["JMA-rec"] if "JMA-rec" in d else '' 
             ncep = d["NCEP-rec"] if "NCEP-rec" in d else '' 
             exp = d["JMA-exp"] if "JMA-exp" in d else d["ECMWF-exp"] if "ECMWF-exp" in d else ''

             data = data+'{},{},{},{},{},{}\n'.format(mydate,exp,ecmwf,jma,ncep,dwd)

          ret = { 'data' : data }

       return ret


def availability_report(request):
    daysback = int(request.GET.get('daysback',7))
    mode = request.GET.get('mode','wdqms')

    dateselects = []
    for i in range(daysback):
         d = date.today() - timedelta(days=i)
         dateselects.append( "( yyyy={} and mm={} and dd={}   )".format( d.year, d.month , d.day  )  )

    wheresqlstring = " or ".join(dateselects)

    if mode=="wdqms":

        sql = """select wigosid,stationname,countrycode,isocc, DATE(yyyy || '-' || mm || '-' || dd) as date,
            sum(nr_expected) as nr_expected, sum(nr_received) as nr_received, sum(nr_used) as nr_used, sum(nr_rejected) as nr_rejected,
            sum(nr_blacklisted) as nr_blacklisted , sum(nr_passive) as nr_passive, center
            from stationsbyperiodex s left join countrymetadata c on (c.vola_code = s.countrycode)
            where ({})
            and varid=110 and stationname not like '%unknown%' and center='ECMWF'
            group by wigosid,stationname,countrycode,isocc,yyyy,mm,dd,center
            order by yyyy,mm,dd,countrycode """.format( wheresqlstring )

        fieldnames = [ "stationId","stationName","countryCode","isoCountryCode","date","NrExpected","NrReceived","NrUsed","NrRejected","NrBlacklisted","NrPassive","center" ]

    elif mode=="smm":  #list number of 6h intervals in which an observation was expected and one came and aggregate by day and station

        sql= """select wigosid,stationname,countrycode,isocc, DATE(yyyy || '-' || mm || '-' || dd) as date,
                count( CASE WHEN nr_expected = 0 THEN NULL ELSE nr_expected END ) as nr_expected,
                ( CASE WHEN nr_received = 0 THEN NULL ELSE nr_received END ) as nr_received, center
                stationsbyperiodex s left join countrymetadata c on (c.vola_code = s.countrycode)
                ( {} )
                and varid=110 and stationname not like '%unknown%' and center='ECMWF'
                group by wigosid,stationname,countrycode,isocc,yyyy,mm,dd,center
                order by yyyy,mm,dd,countrycode """.format( wheresqlstring )

        fieldnames = [ "stationId","stationName","countryCode","isoCountryCode","date","NrExpected","NrReceived","center" ]

    cursor = connection.cursor()
    cursor.execute(sql)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="wdqms.csv"'

    writer = csv.writer(response)
    writer.writerow(fieldnames)
    for row in cursor:
       writer.writerow( row )

    return response

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
    
# this view is used for the station details from the country view
@json_response
def data(request):
    stationindexnbr = request.GET.get('indexnbr')
    wigosid = request.GET.get('wigosid')
    center = request.GET.get('center')
    callback = request.GET.get('callback')

    if wigosid:
    	station = Station.objects.filter(wigosid=wigosid).order_by('-created')[0]
    elif stationindexnbr:
    	station = Station.objects.filter(indexnbr=stationindexnbr).order_by('-created')[0]
    else:
    	raise ValueError("no indexnbr or wigosid supplied")

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
			ss.yyyy, ss.mm, ss.dd, ss.center, v.wigosid  from volaex v join (
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
        wigosid  = row[12]

        myindex = "{}-{}".format(indexnbr,indexsubnbr)

        station = { 'name' : stationname , 'wigosid' : wigosid, 'indexnbr' : myindex , 'nrexp' : nr_ex, 'nrrec' : nr_rec, 'nrrej' : nr_rej , 'nrbla' : nr_bla , 'indexnbr2' : indexnbr }
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

    yesterday = datetime.datetime.now() - timedelta(days=1)
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
    now = datetime.datetime.now()
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
    
