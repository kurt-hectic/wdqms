from wdqms.models import Station
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
from django.contrib.gis.geos import Point
from django.conf import settings

class ImportStations():

    def oscarQuote(self,params):
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


    def run(self):
        self.importStations()
    

    def importStations(self):

        # we import schedules from OSCAR, then obtain a station list from OSCAR. 
        # schedules and stationlist from OSCAR use WIGOS IDs. The WDQMS internal station object also uses a WIGOS ID
        # schedules with a stationID that cannot be matched to the station list are not considered 
        # schedules with one or more empty fields are also not considered

        # get the current stations in the DB. Only get the latest of each station
        current_stations = {}
        for station in Station.objects.order_by('wigosid', '-created').distinct('wigosid'):
            current_stations[station.wigosid]=station

        # get surface pressue stations and schedules from OSCAR
        today = datetime.datetime.today().strftime("%Y%m%d")
        url_pressure_schedules = settings.URL_OSCAR_SCHEDULES.format(today)
        df_oscar_schedules = pd.read_csv(url_pressure_schedules,sep='\t',encoding='latin1',compression='zip')

        params = { 'variable' : "216", 'facilityType' : ['seaFixed','seaMobile','lakeRiverFixed','lakeRiverMobile','landFixed','landMobile','landOnIce','airFixed']}
        param = self.oscarQuote(params)
        url_stations = settings.URL_OSCAR_STATIONS.format(param)
        df_stations = pd.read_json(url_stations).set_index('wmoIndex')

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
        remove_idxs = ~df_oscar_schedules["WMO_INDEX_TX"].isin(  df_stations.index ) 
        print("removing {} schedules which could not be matched to API based search [ {} ]".format( len(df_oscar_schedules[remove_idxs]), df_oscar_schedules[remove_idxs]["WMO_INDEX_TX"] ))
        df_oscar_schedules=df_oscar_schedules[~remove_idxs] 

        # remove empty schedules 
        pd.options.mode.chained_assignment = None
        filter_cols = [ "MONTH_SINCE_NU" , "MONTH_TILL_NU" , "WEEKDAY_SINCE_NU", "WEEKDAY_TILL_NU", "HOUR_SINCE_NU" , "HOUR_TILL_NU", "MINUTE_SINCE_NU" , "MINUTE_TILL_NU"]
        keep_idxs = df_oscar_schedules[filter_cols].notna().all(axis=1) 
        print("removing {} schedules which have empty values".format( len(df_oscar_schedules[~keep_idxs]), df_oscar_schedules[~keep_idxs]["WMO_INDEX_TX"] ))
        df_oscar_schedules = df_oscar_schedules[keep_idxs]
        # convert schedule information to integer
        #df_oscar_schedules.loc[:,filter_cols]  = df_oscar_schedules.loc[:,schedule_cols].astype(int)

        # set empty dataframe cells to None to that Django better handles them in the ORM
        df_stations = df_stations.where( pd.notnull(df_stations) , None )

        # compute number expected based on schedule for all operational stations in oscar schedule list

        # we allow NaN values for minutes and reporting interval.. convert from pandas representation to JSON
        def parseVals(val):
            try:
                return int(val)
            except:
                return ''


        start_time = timeit.default_timer()
        stationschedules = {}
        for idx, row in df_oscar_schedules.iterrows():
            wigosid = row["WMO_INDEX_TX"]
            schedule = {
                'wigosID' : wigosid,
                'operatingStatus' : int(row["OPERATING_STATUS_DECLARED_ID"]),
                'monthFrom' :  int(row["MONTH_SINCE_NU"]) , 'monthTo' : int(row["MONTH_TILL_NU"]),
                'weekFrom' :  int(row["WEEKDAY_SINCE_NU"]) , 'weekTo' : int(row["WEEKDAY_TILL_NU"]),
                'hourFrom' :  int(row["HOUR_SINCE_NU"]) , 'hourTo' : int(row["HOUR_TILL_NU"]),
                'minuteFrom' :  parseVals(row["MINUTE_SINCE_NU"]) , 'minuteTo' : parseVals(row["MINUTE_TILL_NU"]),
                'interval' : parseVals(row["TEMP_REP_INTERVAL_NU"])
            }
        
            if not wigosid in stationschedules:
                stationschedules[wigosid] = { 'schedules' : [] }

            stationschedules[wigosid]['schedules'].append( schedule )

        elapsed = timeit.default_timer() - start_time

        print("computation of schedules of all stations took {} sec".format(elapsed))

        # create objects in the DB
        mapper = { 
            'CXR' : 'AUS',
            'CCK' : 'AUS',
            'ROM' : 'ROU',
            'PRI' : 'USA',
            'GRD' : 'GBR',
            'ESH' : 'MAR',
        }

        counter=0
        error_counter=0
        no_schedule_counter=0
        processed_stations = {}
        for wigosid,station in df_stations.iterrows():
            wigosid="%s" % wigosid
            iso3 = station["iso3"] if not station["iso3"] in mapper else mapper[station["iso3"]]

            # sort schedules to guarante comparable representation in DB
            if wigosid in stationschedules:
                schedulesJson = json.dumps( stationschedules[wigosid]['schedules'] )
            else:
                #print("station {} has no schedule information.. proceeding anyway".format(wigosid))
                schedulesJson = "{}"
            
            s = Station( name=station["name"],wigosid=wigosid, country_id=iso3,
                location=Point( station["longitude"],station["latitude"] ) ,stationtype="SYNOP", region=station["region"],
                schedules = schedulesJson
            )
            processed_stations[wigosid]=True
            if wigosid not in current_stations or current_stations[wigosid] != s : #only insert new object if it is different from previous
                try:
                    s.save()
                    counter+=1
                    if wigosid not in stationschedules:
                        no_schedule_counter+=1
                except IntegrityError as e:
                    error_counter+=1
                    print("cannot save station {}. error: {}".format(s,e))

        # process stations that got closed
        for wigosid,station in current_stations.items():
            if not wigosid in processed_stations and not station.closed: #clone station and set it to closed
                station.pk = None # This is for cloning the station
                station.closed = True
                station.save()

        print("inserted %s new stations" % counter)
        if error_counter>0:
            print("did not insert %s stations due to consistency errors" % error_counter)
        if no_schedule_counter>0:
            print("inserted %s stations with empty schedules" % no_schedule_counter)
