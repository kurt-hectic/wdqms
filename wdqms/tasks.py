from __future__ import absolute_import, unicode_literals
from celery import task
from .models import Station
import psycopg2
import psycopg2.extras
import configparser
import pandas as pd
import calendar
import datetime 
import timeit
import json
import urllib.parse
from urllib.parse import quote
import numpy as np
from collections import namedtuple
import sys,csv,string,time
import re
from datetime import date
import datetime
from django.db import IntegrityError

def mk_float(s):
    s = s.strip()
    return float(s) if s else 0.0

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
        return d

def DMS2DM(degminsec): 
    try:
        (deg,min,sec) = degminsec.split()
    except Exception as e:
        print("error with parsing " + degminsec)
        sys.exit(1)

    sig =  sec[-1:]
    sec = sec[:2]   

    tmp =    int(deg) + int(min) / 60  + int(sec) / 3600

    if re.match( r'[S|W]' , sig): 
        return -1 * tmp
    else:
        return tmp

def oscarQuote(params):
    ret=[]
    for key, value in params.items():
        if isinstance(value,list):
            mykey = urllib.parse.quote(key)
            values = [urllib.parse.quote(v) for v in value]
            myvalue = ",".join(values)
        else:
            mykey=urllib.parse.quote(key)
            myvalue=urllib.parse.quote(value)
            
        ret.append("{}={}".format(mykey,myvalue))

    return "&".join(ret)



def generate_series_for_interval_byperiod( period_date, month_since, month_till, weekday_since , weekday_till, hour_since, hour_till, minute_since, minute_till, interval ):
    
    #list of possible observations on the day of the specificed period (to be grouped into 6h intervals)
    weekday_since=weekday_since-1
    weekday_till=weekday_till-1
    
    medium_dt = datetime.datetime.strptime( "{} {}".format(period_date,0) , "%Y%m%d %H"   )
    lower_dt = medium_dt - datetime.timedelta(hours=3)
    upper_dt = medium_dt + datetime.timedelta(hours=21)
    
    
    # list of possible observations based on schedule and calculated possible years
    current_year = lower_dt.year
    last_day_upper = calendar.monthrange( current_year ,  month_till )[1]
    
    lower_sched_dt = datetime.datetime( lower_dt.year , month_since, 1 , hour_since , minute_since  )
    upper_sched_dt = datetime.datetime( upper_dt.year , month_till, last_day_upper , hour_till , minute_till  )

    Range = namedtuple('Range', ['start', 'end'])    
    
    r1 = Range(start=lower_dt, end=upper_dt)
    r2 = Range(start=lower_sched_dt, end=upper_sched_dt)
    
    latest_start = max(r1.start, r2.start)
    earliest_end = min(r1.end, r2.end)
    
    delta = (earliest_end - latest_start).total_seconds()
    step = int (delta / interval)

    # list of observations in period 
    date_list = [latest_start + datetime.timedelta(seconds=interval) * x for x in range(0,  step   )]
    
    
    # group by hour
    result = { 0 : [] , 6 : [] , 12 : [] , 18 : [] }
    for mydate in date_list:
        key = ((mydate + datetime.timedelta(hours=3)).hour // 6 ) * 6  
        result[ key ].append(mydate)
    
    
    return result


@task()
def task_number_one():
    stations = Station.objects.all()
    print("hello task %s" % len(stations))


@task()
def importStations():

    if not Station.objects.filter(name__contains='unknown'):
        s = Station(name='unknown station',region='unknown',latitude=0,longitude=0,iso3="NUL",wigosid="0-0-0-0",nrExp0=0,nrExp6=0,nrExp12=0,nrExp18=0)
        s.save()

    # get the current stations in the DB. Only get the latest of each station
    current_stations = {}
    for station in Station.objects.order_by('wigosid', '-created').distinct('wigosid'):
        current_stations[station.wigosid]=station

    # get surface pressue stations and schedules from OSCAR
    today = datetime.datetime.today().strftime("%Y%m%d")
    url_pressure_schedules = "https://oscar.wmo.int/oscar/wdqms/surface_pressure_schedules_report-{}.zip".format(today)
    df_oscar_schedules = pd.read_csv(url_pressure_schedules,sep='\t',encoding='latin1',compression='zip')

    params = { 'variable' : "216", 'facilityType' : ['seaFixed','seaMobile','lakeRiverFixed','lakeRiverMobile','landFixed','landMobile','landOnIce','airFixed']}
    param = oscarQuote(params)
    url_station_search = "https://oscar.wmo.int/surface/rest/api/search/station?{}".format(param)
    df_stations = pd.read_json(url_station_search).set_index('wmoIndex')

    # get ISO3 codes
    url_wmo_members = 'http://test.wmocodes.info/wmdr/TerritoryName?_format=csv'
    df_members = pd.read_csv(url_wmo_members).rename(columns = { "dct:description" : "name" ,'rdfs:label' : "iso3" } )
    df_members = df_members[["name","iso3"]]
    df_members["name"] = df_members["name"].apply( lambda x: x.split('@')[0].strip('\'').replace('\\\'','\'') )
    df_members = df_members.set_index('iso3')
    df_members.loc['SWZ','name'] = 'Eswatini'

    # join ISO3 codes to stations
    df_stations = df_stations.join( df_members.reset_index().set_index('name') , on='territory' )

    df_missing = df_stations[ df_stations["iso3"].isnull() ][["name","territory"]] 
    if len(df_missing)>0:
        print("warning: the following stations could not be mapped to an ISO code %s " % df_missing)

    # remove schedules for which we do not have corresponding station info
    df_oscar_schedules=df_oscar_schedules[df_oscar_schedules["WMO_INDEX_TX"].isin(  df_stations.index ) ]

    # remove empty schedules and convert to int
    pd.options.mode.chained_assignment = None
    filter_cols = [ "MONTH_SINCE_NU" , "MONTH_TILL_NU" , "WEEKDAY_SINCE_NU", "WEEKDAY_TILL_NU", "HOUR_SINCE_NU" , "HOUR_TILL_NU", "MINUTE_SINCE_NU" , "MINUTE_TILL_NU", "TEMP_REP_INTERVAL_NU"]
    df_oscar_schedules = df_oscar_schedules[df_oscar_schedules[filter_cols].notna().all(axis=1)]
    df_oscar_schedules.loc[:,filter_cols]  = df_oscar_schedules.loc[:,filter_cols].astype(int)

    # set empty dataframe cells to None to that Django better handles them in the ORM
    df_stations = df_stations.where( pd.notnull(df_stations) , None )

    # compute number expected based on schedule for all operational stations in oscar schedule list

    start_time = timeit.default_timer()
    stationobservations = {}
    for index, row in df_oscar_schedules.iterrows():
        if row["OPERATING_STATUS_DECLARED_ID"]:
            idx = row["WMO_INDEX_TX"]
            observations = generate_series_for_interval_byperiod(today, row["MONTH_SINCE_NU"] , row["MONTH_TILL_NU"] , 
                row["WEEKDAY_SINCE_NU"] , row["WEEKDAY_TILL_NU"] , 
                row["HOUR_SINCE_NU"] , row["HOUR_TILL_NU"],
                row["MINUTE_SINCE_NU"] , row["MINUTE_TILL_NU"],
                row["TEMP_REP_INTERVAL_NU"]
                )

        if idx in stationobservations:
            for p in [0,6,12,18]:
                stationobservations[idx][p] = stationobservations[idx][p].union( set(observations[p]) )
        else:
            stationobservations[idx] = {}
            for p in [0,6,12,18]:
                stationobservations[idx][p] = set(observations[p])    

    elapsed = timeit.default_timer() - start_time

    print("computation of schedules of all stations took {} sec".format(elapsed))

    # assign default values for nr. expected for stations in OSCAR
    DEFAULT_NR_EXPECTED = 2 #assume 3 hourly observations 
    df_stations["Nr Exp 0"] = DEFAULT_NR_EXPECTED
    df_stations["Nr Exp 6"] = DEFAULT_NR_EXPECTED
    df_stations["Nr Exp 12"] = DEFAULT_NR_EXPECTED
    df_stations["Nr Exp 18"] = DEFAULT_NR_EXPECTED

    # now assign values 
    for idx,obs in stationobservations.items():
        for p in [0,6,12,18]:
            df_stations.loc[idx,"Nr Exp %s" % p] = len(obs[p])
    
    # create objects in the DB
    counter=0
    error_counter=0
    for idx,station in df_stations.iterrows():
        wigosid="%s" % idx
        s = Station( name=station["name"],wigosid=wigosid, iso3=station["iso3"], latitude=station["latitude"],
            longitude=station["longitude"],stationtype="SYNOP", region=station["region"],
            nrExp0=station["Nr Exp 0"], nrExp6=station["Nr Exp 6"], nrExp12=station["Nr Exp 12"], nrExp18=station["Nr Exp 18"]
        )
        if wigosid not in current_stations or current_stations[wigosid] != s : #only insert new object if it is different from previous
            try:
                s.save()
                counter+=1
            except IntegrityError as e:
                error_counter+=1
                print("cannot save station {}. error: {}".format(s,e))


    print("inserted %s new stations" % counter)
    if error_counter>0:
        print("did not insert %s stations due to consistency errors" % error_counter)
