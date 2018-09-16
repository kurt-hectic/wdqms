from django.db import models 
from django.utils import timezone
from datetime import date
import datetime
from django.utils import timezone

class Station(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    wigosid = models.CharField(max_length=200)
    iso3 = models.CharField(max_length=3,blank=True,null=True)
    region = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()
    stationtype = models.CharField(max_length=10)
    nrExp0 = models.IntegerField()
    nrExp6 = models.IntegerField()
    nrExp12 = models.IntegerField()
    nrExp18 = models.IntegerField()
    created = models.DateTimeField(blank=True,default=timezone.now)

    def __eq__(self,other):
        location_self = "{:4.5f} {:4.5f}".format(self.latitude,self.longitude)
        location_other = "{:4.5f} {:4.5f}".format(other.latitude,other.longitude)

        if location_self != location_other:
            print("{} different location {} {}".format(self.wigosid,location_self,location_other))

        cmpattr = ['name','wigosid','iso3','region','nrExp0','nrExp6','nrExp12','nrExp18']

        for ca in cmpattr:
            if getattr(self,ca) != getattr(other,ca):
                print("{}: {} and {} unequal {}".format(ca,getattr(self,ca),getattr(other,ca),self.wigosid))
                return False

        if location_self != location_other :
            print("location: {} and {} unequal {}".format(location_self,location_other,self.wigosid))
            return False
    
        return True


    def __str__(self):
        return "{} {} {}".format(self.wigosid,self.name,self.created)


    class Meta:
        db_table='station'
        managed=True

        def __str__(self):
            return "name: {} idx: {}  created:{}".format(self.name,self.wigosid,self.created)


class Country(models.Model):
    code = models.CharField(db_column='cc',max_length=3,primary_key=True)
    name = models.CharField(max_length=100)
    _bounding_box = models.CharField(db_column='extent',max_length=5000)
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
    filetype = models.CharField(max_length=5)
    date = models.DateField(db_column='mydate')


    class Meta:
        db_table = 'period'
        managed = True
        ordering = ['date','center','filetype']

    def __str__(self):
        return "{}-{}-{}".format(self.date,self.center,self.filetype)

