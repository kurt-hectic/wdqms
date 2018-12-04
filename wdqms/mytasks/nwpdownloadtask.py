from django.conf import settings
import os,sys,io
import logging
from wdqms.models import Station, Period, Observation, NrObservation
import pandas as pd
import traceback
import gzip
import re
import json
import calendar
from collections import namedtuple
import datetime
from timeit import default_timer as timer
from django.contrib.gis.geos import Point
from django.db import transaction
from django.db import connection
import pytz

pd.set_option('display.height', 1000)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 1500)
pd.set_option('display.width', 1200)


# TODO: guess NWP center from fileargs .. also, process fileargs
class NwpDownloadTask:

    def opener(self,filename):
        if ( filename.endswith(".gz") ):
            return gzip.open(filename,"rt",newline='\n')
        else:
            return open(filename)


    def __init__(self):
        self.unknownstations = []
        self.ignoredstations = []
        self.ignoredobservations = 0
        self.ignorefiles = []

        self.log = logging.getLogger(__name__)
        out_hdlr = logging.StreamHandler(sys.stdout)
        out_hdlr.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
        out_hdlr.setLevel(logging.INFO)
        self.log.addHandler(out_hdlr)
        self.log.setLevel(logging.INFO)

        self.scheduleCache = {}

        self.column_mapper = { 'nr_rec_0' : 'nr_used' , 'nr_rec_1' : 'nr_not_used' ,  'nr_rec_2' : 'nr_rejected' ,  
                  'nr_rec_3' : 'nr_never_used' , 'nr_rec_4' : 'nr_thinned' , 'nr_rec_5' : 'nr_rejected_da' , 
                  'nr_rec_6' : 'nr_used_alt' , 'nr_rec_7': 'nr_quality_issue' , 'nr_rec_8' : 'nr_other_issue' , 'nr_rec_9' : 'nr_no_content' }

        empty_station = Station.objects.filter(name='unknown station',wigosid='0-0-0-0')
        if len(empty_station) > 1:
            raise Exeption("too many empty station stubs in DB")
    
        if len(empty_station) == 1 :
            empty_station = empty_station[0]
        else:
            empty_station = Station(name='unknown station', country=None , wigosid='0-0-0-0', region='unknown', closed=True, stationtype='unknown', location=Point(0,0) )
            empty_station.save()    
        self.empty_station_id = empty_station.id
        
        self.oscar_cols = ["id","latitude","longitude","wigosid","id","nr_expected"]
        self.batch_size = 1000

    def calculateNrObservations(self, period_date, schedules):

        def makeScheduleKey(schedule):
            return "{monthFrom}-{monthTo}-{weekFrom}-{weekTo}-{hourFrom}-{hourTo}-{minuteFrom}-{minuteTo}-{interval}".format(**schedule)

        observations = []

        for schedule in schedules:

            operatingStatus = int(schedule["operatingStatus"])
            if not operatingStatus:
                continue

            key = makeScheduleKey(schedule)
            if key in self.scheduleCache:
                observations.extend( self.scheduleCache[key] )
                continue

            try:
                weekday_since=int(schedule["weekFrom"])-1
                weekday_till=int(schedule["weekTo"])-1
                month_since=int(schedule["monthFrom"])
                month_till=int(schedule["monthTo"])
                hour_since=int(schedule["hourFrom"])
                hour_till=int(schedule["hourTo"])
                minute_since=int(schedule["minuteFrom"])
                minute_till=int(schedule["minuteTo"])
                interval = int(schedule["interval"])
            except:
                #print("schedule {} invalid".format(schedule))
                continue

            # upper and lower boundaries of the indicated 6h period TODO: check if this corresponds to the agreed time windows
            medium_dt = period_date
            lower_dt = medium_dt - datetime.timedelta(hours=3)
            upper_dt = medium_dt + datetime.timedelta(hours=3)

            # now we calculate the list of possible observations based on schedule and calculated possible years
            # first we need upper and lower boundaries of the schedule..        
            # years are based on the date of the 6h period (since years are not in the schedule we need to approximate.. one solution could be to fetch historic deployments from OSCAR)
            timezone = pytz.timezone("UTC")
            current_year = lower_dt.year
            last_day_upper = calendar.monthrange( current_year ,  month_till )[1]
            lower_sched_dt = pytz.utc.localize(datetime.datetime( lower_dt.year , month_since, 1 , hour_since , minute_since  ))
            upper_sched_dt = pytz.utc.localize(datetime.datetime( upper_dt.year , month_till, last_day_upper , hour_till , minute_till  ))

            # we use ranges to identify the period of time where current 6h period and schedule overlap
            Range = namedtuple('Range', ['start', 'end'])
            r1 = Range(start=lower_dt, end=upper_dt)
            r2 = Range(start=lower_sched_dt, end=upper_sched_dt)
            latest_start = max(r1.start, r2.start)
            earliest_end = min(r1.end, r2.end)

            # now we can check how many seconds are in the overlapping period and calculate a stepsize which we use to generate actual observations
            delta = (earliest_end - latest_start).total_seconds()
            step = int (delta / interval)
            # genrate observations
            date_list = [latest_start + datetime.timedelta(seconds=interval) * x for x in range(0,  step   )]

            observations.extend(date_list)
            self.scheduleCache[key] = date_list

        return len(set(observations))


    def updateDBstats(self):

        sql = """INSERT INTO dbstats(createdate,oid,table_schema,table_name,row_estimate,total_bytes,index_bytes,toast_bytes,table_bytes,total,index,toast,"table")
          SELECT %s as createdate, *, pg_size_pretty(total_bytes) AS total
            , pg_size_pretty(index_bytes) AS INDEX
            , pg_size_pretty(toast_bytes) AS toast
            , pg_size_pretty(table_bytes) AS TABLE
          FROM (
          SELECT *, total_bytes-index_bytes-COALESCE(toast_bytes,0) AS table_bytes FROM (
              SELECT c.oid,nspname AS table_schema, relname AS TABLE_NAME
                      , c.reltuples AS row_estimate
                      , pg_total_relation_size(c.oid) AS total_bytes
                      , pg_indexes_size(c.oid) AS index_bytes
                      , pg_total_relation_size(reltoastrelid) AS toast_bytes
                  FROM pg_class c
                  LEFT JOIN pg_namespace n ON n.oid = c.relnamespace
                  WHERE relkind = 'r'
          ) a
        ) a where table_schema = 'public'
        order by total_bytes desc """

        with connection.cursor() as cursor:
            params = (datetime.datetime.now(),)
            cursor.execute(sql,params)


    def processHeaders(self,headers):
        headers.pop() #remove last header.. it is the fieldname

        myheaders = {}

        for header in headers:
            header = header.replace('StatusFlag:','StatusFlag=')
            header = header.replace('Status flag:','Status flag=')
            (key,val) = re.split(r'[=]', header)
            key=key.lstrip('#').lstrip()
            val=val.rstrip().lstrip()
            myheaders[key]=val  

        return myheaders

    def checkMD(self,md,myheaders):

        center=md["center"]
        filetype=md["filetype"]
        mydate = md["date"]

        Period.objects.filter(filetype=filetype , center=center , date=mydate)[0]

        return cnt == 0

    def getStations(self,date):
        current_stations = {}
        #for station in Station.objects.filter(closed=False,created__lte=date).order_by('wigosid', '-created').distinct('wigosid'): #FIXME: stations to be loaded as at time of current 6h period (insert additional filter condition?)
        for station in Station.objects.filter(closed=False).order_by('wigosid', '-created').distinct('wigosid'): #FIXME: stations to be loaded as at time of current 6h period (insert additional filter condition?)
            schedules = json.loads( station.schedules )
            nr_expected = self.calculateNrObservations( date , schedules )

            current_stations[station.wigosid]= { 'wigosid' : station.wigosid , 'id' : station.id , 'name' : station.name , 
                                                    'latitude' : station.location.coords[1] , 'longitude' : station.location.coords[0] ,
                                                    'nr_expected' : nr_expected   }

        df_oscar = pd.DataFrame.from_dict( current_stations , orient='index' )
        if len(df_oscar) == 0:
            raise Exception("no stations in DB ")
        df_oscar.id = df_oscar.id.astype(int)

        # extract last WIGOS ID block as identifier 
        df_oscar["local_idx"] = df_oscar["wigosid"].str.split('-').str[3]

        return df_oscar 

    def processLines(self,sio,metadata): # need idx of first data row

        print("process line..")

        # create dataframe for processing 
        dtypes = { 'station_id' : str , 'yyyymmdd': str , 'hhmmss' : str , 'latitude' : float , 'longitude' : float ,
            'statusflag' : int , 'centre_id' : str, 'var_id' : int , 'bg_dep' : float , 
            'mean_bg_dep' : float , 'std_bg_dep':float , 'levels': str  ,'lastreplevel' : float , 'codetype' : int  }

        df_observations = pd.read_csv(sio,dtype=dtypes, na_values={'bg_dep': '******'})
        df_observations["obsdate"] = pd.to_datetime(df_observations['yyyymmdd'] + ' ' + df_observations['hhmmss'].str.strip(), format="%Y%m%d %H%M%S")
        df_observations["obsdate"] = df_observations["obsdate"].dt.tz_localize('UTC')
        df_observations["centre_id"] = df_observations["centre_id"].str.upper().replace('ECMF','ECMWF')
        sio.close()
        nr_obs = len(df_observations)

        # get the current stations in the DB. Only get the latest of each station

        df_oscar = self.getStations(metadata["date"])
        df_oscar = df_oscar.set_index(['local_idx']) #FIXME: risk of duplicates here

        nr_oscar=len(df_oscar)

        if not "var_id" in df_observations.columns :
            df_observations["var_id"] = metadata["variable"]

        # only process accepted variables
        idx_accepted = df_observations["var_id"].isin( metadata["acceptedvariables"] )
        df_ignored_obs = df_observations[ ~idx_accepted  ]
        df_observations = df_observations[ idx_accepted ]

        # remove observations that do not have an integer station ID TODO: this may be revisited
        idx_not_int = pd.to_numeric( df_observations["station_id"] , errors='coerce'  ).isna() 
        df_ignored_stations = df_observations[ idx_not_int ] 
        df_observations = df_observations[ ~idx_not_int ]
        
        #fix some old NCEP data
        if metadata["center"] == "NCEP" and metadata["date"] < datetime.datetime(2015,12,3):
            print("correcting latitude")
            df_observations["latitude"] = - (360 - df_observations["latitude"])


        # match observations with stations. local_idx (extracted from OSCAR WIGOS ID) and station_id (from NWP file) as join keys
        suffix = '_oscar'
        df_observations = df_observations.join( df_oscar[self.oscar_cols] , on='station_id' , how='left' , rsuffix=suffix ).reset_index()
        nr_obs = len(df_observations)

        for df in [df_observations]:
            # identify stations in OSCAR and copy location. set id of empty station for stations not in OSCAR
            # OSCAR coordinates are more authorative. If we have no match we use what was reported in the message
            idx_not_in_oscar = df['wigosid'].isna()
            df.loc[ idx_not_in_oscar ,'id'] = self.empty_station_id
            df.loc[ idx_not_in_oscar ,'name'] = "Unknown"

            #df.loc[ ~idx_not_in_oscar , ["latitude","longitude"]] = df.loc[ ~idx_not_in_oscar , ["latitude"+suffix,"longitude"+suffix]].astype(float)
            df.loc[ ~idx_not_in_oscar , 'latitude' ] = df.loc[ ~idx_not_in_oscar , 'latitude_oscar' ]
            df.loc[ ~idx_not_in_oscar , 'longitude' ] = df.loc[ ~idx_not_in_oscar , 'longitude_oscar' ]


            #print( df[ ~idx_not_in_oscar ][["latitude"+suffix,"longitude"+suffix]] )
            df["invola"] = ~idx_not_in_oscar 
            # df.loc[~idx_not_in_oscar , "invola"]=True 
            # df.loc[ idx_not_in_oscar , "invola"]=False
            df.loc[ idx_not_in_oscar , "wigosid"] = df[ idx_not_in_oscar ]["station_id"]
            # TODO: ready to be inserted into DB (obs table)
            #print( df[ df[['latitude','longitude']].isnull().any(axis=1) ] )


        print("len oscar %s len obs %s len  len ignored_stat %s len ignoed obs %s" % ( nr_oscar , nr_obs , len(df_ignored_stations),len(df_ignored_obs)))



        df_observations = df_observations[['centre_id','var_id','obsdate','statusflag','bg_dep','latitude','longitude','id','wigosid']]
        df_observations = df_observations.loc[:,~df_observations.columns.duplicated()]

        print("insert objects into DB")
        with transaction.atomic():
            p = Period(filetype=metadata["filetype"],center=metadata["center"],date=metadata["date"],processed=False)
            p.save()
            observations = []
            df_observations=df_observations.where( (pd.notnull(df_observations)), None)
            #df_observations.where( (pd.notnull(df_observations)), None)
            #pd.notnull(df_observations)
            for idx,row in df_observations.iterrows():
                observations.append( Observation(
                            center=row["centre_id"],
                            varid=row["var_id"],
                            observationdate=row["obsdate"],
                            period=p,
                            status=row["statusflag"],
                            bg_dep=row["bg_dep"],
                            location=Point( row["longitude"],row["latitude"] ),
                            station_id = row["id"], 
                            wigosid = row["wigosid"], 
                ) )


            
            Observation.objects.bulk_create( observations , batch_size = self.batch_size )
            self.updateDBstats()

        print("end process line")


    def processFile(self,name,center,filetype):

        if center=="NCEP" and "ncepdemo.csv" in name:
            return False

        with self.opener(name) as f:

            headers = []
            headersection = True        
            sio = io.StringIO()
            is_header=True
            for line in f:
                if line[:1] == '#':
                    headers.append(line)
                    header_line=line
                else:
                    if is_header:
                        is_header=False
                        hl = header_line.lower().replace('statioin_id','station_id').replace('#','').replace('o-b','bg_dep').replace('mean_bg_dep','bg_dep') #unify headers
                        sio.write( hl ) #write last header line into buffer to have headers

                    sio.write(line)

            f.close()
            sio.seek(0)
        
        myheaders=self.processHeaders(headers)

        if not "An_date" in myheaders or not re.search('\d{8}',myheaders["An_date"])  :
            if center == "NCEP":
                m = re.search('(\d{8})',name)
                myheaders["An_date"] = m.group(0)
                #print("using filename based date {}".format(myheaders["An_date"]))
            else:
                raise Exception("required headers not present","")

        if not "An_time" in myheaders :
            if center == "NCEP":
                m = re.search('t(\d{2})z',name)
                myheaders["An_time"] = m.group(0)
                #print("using filename based time {}".format(myheaders["An_time"]))
            else:
                raise Exception("required headers not present","")

        #print("we have header {} {} ".format(myheaders["An_date"],myheaders["An_time"]))

        # TODO: check if these values are ok
        yyyy = int(myheaders["An_date"][:4])
        mm = int(myheaders["An_date"][4:6])
        dd = int(myheaders["An_date"][6:8])
        period = int(myheaders["An_time"].replace('z','').replace('t',''))
        assimilationdate = pytz.utc.localize(datetime.datetime(yyyy,mm,dd,period,0,0))

        if filetype == "SYNOP":
            varId=110
            acceptedVars = [110,1]
        elif filetype == "TEMP":
            varId=3
            acceptedVars = [2,3,4,29]

        metadata = { 'center' : center.upper() , 'variable' : varId , 'acceptedvariables' : acceptedVars  , 'filetype' : filetype , 'date' : assimilationdate}

        p = Period.objects.filter(filetype=filetype , center=metadata["center"] , date=metadata["date"])

        if len(p)==0:

            stats = { "filename" : name }
            start = timer()
            self.processLines(sio,metadata) # need idx of first data row
            sio.close()
            end = timer()
            stats["processlines"] = (end - start)

        else:
            print(os.path.basename(name) + " already imported")
            return False

        return True


    def metaProcessFile(self,file,center):

        if not (file.endswith(".csv") or file.endswith(".gz")):
            return

        print("process %s %s " % (file,center ))

        filetype = "SYNOP"
        if "_TEMP_" in str(file):
            filetype = "TEMP"

        try:
            if self.processFile(file,center,filetype) :
                self.log.info("imported {} unknown stations: {} , ignored: {}, ignored obs: {}".format(file,len(list(set(self.unknownstations))),len(self.ignoredstations),self.ignoredobservations))
        
        except Exception as e:
            self.log.error("problem with {} .. {} not imported".format(file,str(e)))
            traceback.print_exc()


    def run(self,files=None):
        cmdfiles = []

        config = settings.WDQMS
        try:
            with open(config["IMPORTER"]['IGNORE_FILE'],'r') as f:
                self.ignorefiles = f.read().splitlines()
        except: 
            self.log.warning("IGNORE file not configured")  
            self.ignorefiles = []
    
        dataroot = config['IMPORTER']['PATH']
        
        datadirs = {
            "NCEP": dataroot +"/"+config['DATADIRS']['NCEP'],
            "DWD": dataroot +"/"+config['DATADIRS']['DWD'],
            "JMA": dataroot +"/"+config['DATADIRS']['JMA'],
            "ECMWF": dataroot +"/"+config['DATADIRS']['ECMWF'],
        };
        enabled_centers = config['IMPORTER']['ENABLED_NWP_CENTERS']
        
        
        for center,ddir in datadirs.items():
            if center not in enabled_centers:
                continue
            # traverse root directory, and list directories as dirs and files as files
            for root, dirs, files in os.walk(ddir):
                path = root.split('/')
                for file in files :
                    if file in self.ignorefiles:
                        log.info("ignoring file {} ".format(file))
                        continue
                    name = os.path.join(root, file)
                    self.metaProcessFile(name,center)
                    #return #FIXME: just process one file


        self.processIntervals()


    def processIntervals(self):

        ready_to_process = []
        periods = Period.objects.order_by('center','filetype','-date')
        l = len(periods)

        for index,period in enumerate(periods):
            if period.processed: # do not consider when already processed
                continue
            if period.center in ['JMA','NCEP']: # JMA and NCEP files can be processed without preconditions
                ready_to_process.append(period)
            if period.center in ['ECMWF','DWD']: # ECMWF and DWD need the previous file to be there
                if index + 1 < l:
                    previous = periods[index+1]
                    if period.date - datetime.timedelta(hours=6) == previous.date and period.center == previous.center and period.filetype == previous.filetype:
                        ready_to_process.append(period)
                

        for period in ready_to_process:
            self.aggregateObservationInterval(period)
            


    def aggregateObservationInterval(self,period):
    
        print("aggregating {}".format(period))

        # upper and lower boundaries of integration interval
        date_lower =  period.date - datetime.timedelta( hours=3 )
        date_upper =  period.date + datetime.timedelta( hours=3 ) - datetime.timedelta( milliseconds=1 ) # exclude upper boundary
        date_range = [date_lower, date_upper]

        # get observations from DB for the integration interval 
        observations = Observation.objects.filter( center = period.center , period__filetype = period.filetype , observationdate__range = date_range )
        df_observations = pd.DataFrame( list( observations.values('center','varid','observationdate','status','bg_dep','station_id','location','wigosid','period_id') ) )
        df_observations["latitude"] = [ coord[1] for coord in df_observations['location'] ]
        df_observations["longitude"] = [ coord[0] for coord in df_observations['location'] ]


        # aggregate by station, get total number received and mean background departure
        df_obs_total = df_observations.groupby(['wigosid','station_id','varid','center']).agg( 
                {'varid' : 'count' , 'bg_dep' : 'mean' , 'latitude' : 'first' ,  'longitude' : 'first'    } )
        df_obs_total.rename(inplace=True, columns={ 'varid': 'nr_received' , 'bg_dep' : 'avg_bg_dep'} )

        # aggregate by station and statusflag to get number by statusflag
        df_obs_agg = df_observations.groupby( ['wigosid','station_id','status','varid','center'] )['bg_dep'].count().reset_index()
        df_obs_agg = df_obs_agg.set_index(['wigosid','station_id','varid','center','status'])
        df_obs_agg = df_obs_agg.unstack(level=-1) # transpose the groups to get rows as columns
        df_obs_agg.columns=[ "nr_rec_{}".format(x[1])  for x in df_obs_agg.columns.ravel()]
        df_obs_agg.rename( inplace=True, columns=self.column_mapper )
        df_obs_agg["isempty"] = False

        # combine aggregation by status with overall number received and background departures
        df_obs_agg = df_obs_agg.join( df_obs_total  )
        df_obs_agg = df_obs_agg.reset_index()

        df_obs_agg["assimilationdate"] = period.date

        # join with OSCAR info 
        df_oscar = self.getStations(period.date)
        df_oscar = df_oscar.reset_index()
        df_oscar = df_oscar.set_index('id') #FIXME: risk of duplicates here
        suffix = "_oscar"
        #print(df_oscar)
        #df_obs_agg=df_obs_agg.join(df_oscar[self.oscar_cols] , on='station_id' , how='left', rsuffix=suffix) 
        df_obs_agg=df_obs_agg.join(df_oscar , on='station_id' , how='left', rsuffix=suffix) 

        # stations that are not in OSCAR 
        idx_not_in_oscar = df_obs_agg["station_id"] == self.empty_station_id
        df_obs_agg["invola"] = ~idx_not_in_oscar
        df_obs_agg.loc[ ~idx_not_in_oscar , 'latitude' ] = df_obs_agg.loc[ ~idx_not_in_oscar , 'latitude_oscar' ]
        df_obs_agg.loc[ ~idx_not_in_oscar , 'longitude' ] = df_obs_agg.loc[ ~idx_not_in_oscar , 'longitude_oscar' ]

        # empty stations 
        df_report_expected = df_oscar[df_oscar["nr_expected"] > 0].set_index('wigosid') # stations which we expected at least a report from
        df_not_reporting = df_report_expected.join( df_observations.set_index('wigosid')["observationdate"] ,how='left') # remove those stations which did report (a variable we expected)
        df_not_reporting = df_not_reporting[ df_not_reporting["observationdate"].isna() ]
        df_not_reporting.loc[:,"nr_received"] = 0  
        df_not_reporting.loc[:, "invola"] = True
        df_not_reporting.loc[:, "isempty"] = True
        df_not_reporting.loc[:, "hasduplicate"] = False
        df_not_reporting.loc[:, "center"] =  period.center
        df_not_reporting.loc[:, "varid"] =  110 # FIXME: make dynamic metadata["variable"]
        df_not_reporting.rename( columns={'observationdate':'assimilationdate'} , inplace=True)
        df_not_reporting["assimilationdate"] = period.date

        df_obs_agg =  pd.concat( [df_obs_agg , df_not_reporting] )

        # mark duplicates TODO: need to test this
        if period.filetype == "SYNOP": 
            df_duplicate = df_obs_agg.reset_index().set_index('station_id')
            duplicates = df_duplicate[df_duplicate["varid"]==110].join( df_duplicate[ df_duplicate["varid"]==1 ], how='inner' , lsuffix="_left").index.tolist()
            df_obs_agg["hasduplicate"] = ( df_obs_agg.index.isin( duplicates ) ) & ( df_obs_agg["varid"] == 1 )

        observations_nr = []
        fields =  self.column_mapper.values()


        df_obs_agg=df_obs_agg.where( df_obs_agg.notnull(), None)
        for idx,row in df_obs_agg.reset_index().iterrows():
            no = NrObservation(
                        center=row["center"],
                        varid=row["varid"],
                        assimilationdate=row["assimilationdate"],
                        period=period,
                        bg_dep=row["avg_bg_dep"],
                        location=Point( row["longitude"],row["latitude"] ),
                        station_id = row["station_id"], 
                        wigosid = row["wigosid"], 
                        invola = row["invola"],
                        isempty = row["isempty"],
                        hasduplicate = row["hasduplicate"],
                        nr_expected = row["nr_expected"] ,
                        nr_received = row["nr_received"] 
            )
            for field in fields:
                if field in row:
                    setattr(no,field,row[field])

            observations_nr.append( no )

        NrObservation.objects.bulk_create( observations_nr , batch_size = self.batch_size )

        period.processed = True
        period.save()
