from django.contrib.gis.db import models
from django.utils import timezone
from datetime import date
import datetime
import json
from django.utils import timezone


class Station(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    wigosid = models.CharField(max_length=200)
    #iso3 = models.CharField(max_length=3,blank=True,null=True)
    region = models.CharField(max_length=200)
    stationtype = models.CharField(max_length=10)
    schedules = models.TextField()
    closed = models.BooleanField(default=False)
    created = models.DateTimeField(blank=True,default=timezone.now)
    country = models.ForeignKey("Country",db_column='iso3',null=True,on_delete=models.SET_NULL,)
    location = models.PointField(db_column='geom')

    def __eq__(self,other):
        location_self = "{:4.5f} {:4.5f}".format(self.location.coords[0],self.location.coords[1])
        location_other = "{:4.5f} {:4.5f}".format(other.location.coords[0],other.location.coords[1])

        if location_self != location_other:
            print("{} different location {} {}".format(self.wigosid,location_self,location_other))
            return False

        cmpattr = ['name','wigosid','country','region','closed']

        for ca in cmpattr:
            if getattr(self,ca) != getattr(other,ca):
                print("{}: {} and {} unequal {}".format(ca,getattr(self,ca),getattr(other,ca),self.wigosid))
                return False

        schedules_self = json.loads( self.schedules )
        schedules_other = json.loads( other.schedules )
        if schedules_self != schedules_other:
            print("{}: schedules different. {} vs. {}.".format(self.wigosid,schedules_self,schedules_other))
            return False
    
        return True


    def __str__(self):
        return "{} {} {}".format(self.wigosid,self.name,self.created)


    class Meta:
        db_table='station'
        managed=True

        def __str__(self):
            return "name: {} idx: {}  created:{}".format(self.name,self.wigosid,self.created)


class Observation(models.Model):

    id = models.AutoField(primary_key=True)
    center = models.CharField(max_length=10)
    varid = models.PositiveSmallIntegerField()
    observationdate = models.DateTimeField()
    location = models.PointField(db_column='geom')
    status = models.PositiveSmallIntegerField()
    bg_dep = models.FloatField(null=True)
    wigosid = models.CharField(max_length=200,null=True,blank=True)

    station = models.ForeignKey(
        'Station',
        null=True, blank=True,
        on_delete=models.SET_NULL,
    )
    period = models.ForeignKey(
        'Period',
        on_delete=models.CASCADE
    )
    
    class Meta:
        db_table='nwpdata'

class NrObservation(models.Model):

    id = models.AutoField(primary_key=True)
    center = models.CharField(max_length=10)
    varid = models.PositiveSmallIntegerField()
    assimilationdate = models.DateTimeField()
    wigosid = models.CharField(max_length=200,null=True,blank=True)
    location = models.PointField(db_column='geom')
    invola = models.BooleanField()
    isempty = models.BooleanField()
    hasduplicate = models.BooleanField()
    bg_dep = models.FloatField(null=True)
    nr_expected = models.PositiveSmallIntegerField(null=True)
    nr_received = models.PositiveSmallIntegerField(null=True)
    nr_used = models.PositiveSmallIntegerField(null=True)
    nr_not_used = models.PositiveSmallIntegerField(null=True)
    nr_rejected = models.PositiveSmallIntegerField(null=True)
    nr_never_used = models.PositiveSmallIntegerField(null=True)
    nr_thinned = models.PositiveSmallIntegerField(null=True)
    nr_rejected_da = models.PositiveSmallIntegerField(null=True)
    nr_used_alt = models.PositiveSmallIntegerField(null=True)
    nr_quality_issue = models.PositiveSmallIntegerField(null=True)
    nr_other_issue = models.PositiveSmallIntegerField(null=True)
    nr_no_content = models.PositiveSmallIntegerField(null=True)
    station = models.ForeignKey(
        'Station',
        null=True, blank=True,
        on_delete=models.SET_NULL,
    )
    period = models.ForeignKey(
        'Period',
        on_delete=models.CASCADE
    )

    def __str__(self):
        return "station_id: {} wid: {} invola:{} nr_ex:{} nr_rec: {} date: {} center: {}".format(self.station_id,self.wigosid,self.invola,self.nr_received,self.nr_expected,self.assimilationdate,self.center)

    class Meta:
        db_table='nwpdatabyperiod'
        indexes = [ models.Index(fields=['assimilationdate',]) , models.Index(fields=['center',]) ,  models.Index(fields=['location',])] 

class Country(models.Model):
    code = models.CharField(db_column='cc',max_length=3,primary_key=True)
    name = models.CharField(max_length=100)
    _bounding_box = models.CharField(db_column='extent',max_length=5000) #TODO: convert to geom
    vola_code = models.IntegerField(null=True,blank=True)

    class Meta:
        db_table='country'
        managed=True

    def __str__(self):
        return "{} ({}) : vola:{} location: {}".format(self.name,self.code,self.vola_code,self._bounding_box)


    @property
    def bounding_box(self):

        bbox = self._bounding_box.replace('POLYGON((','').replace('))','')
        coords = bbox.split(',')

        minlon = coords[0].split(' ')[1]
        maxlon = coords[1].split(' ')[1]
        minlat = coords[0].split(' ')[0]
        maxlat = coords[2].split(' ')[0]

        return { 'minlat' : minlat, 'minlon' : minlon , 'maxlat' : maxlat, 'maxlon' : maxlon }


class Period(models.Model):
    center = models.CharField(max_length=10)
    date = models.DateTimeField(db_column='mydate')
    filetype = models.CharField(max_length=20)
    processed = models.BooleanField(default=False)

    class Meta:
        db_table = 'period'
        managed = True
        ordering = ['date','center','filetype']

    def __str__(self):
        return "{}-{}-{}".format(self.date.strftime('%Y-%m-%d-%H'),self.center,self.filetype)

    def __eq__(self,other):
        return self.center == other.center and self.filetype == other.filetype and self.date == other.date and self.processed == other.processed 

        


class DBStats(models.Model):

    createdate = models.DateTimeField(default=datetime.datetime.now)
    oid = models.IntegerField(null=True)
    table_schema = models.CharField(max_length=20,null=True)
    table_name = models.CharField(max_length=50,null=True)
    row_estimate = models.FloatField(null=True)
    total_bytes = models.BigIntegerField(null=True)
    index_bytes = models.BigIntegerField(null=True)
    toast_bytes = models.BigIntegerField(null=True)
    table_bytes = models.BigIntegerField(null=True)
    total = models.CharField(max_length=50,null=True)
    index = models.CharField(max_length=50,null=True)
    toast = models.CharField(max_length=50,null=True)
    table = models.CharField(max_length=50,null=True)

    class Meta:
        db_table = 'dbstats'
