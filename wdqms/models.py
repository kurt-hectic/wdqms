from django.db import models 
from django.utils import timezone
from datetime import date

class Station(models.Model):
	name = models.CharField(max_length=200,db_column='stationname')
	indexnbr = models.IntegerField(db_column='indexnbr')
	subindexnbr = models.IntegerField(db_column='indexsubnbr')
	wigosid = models.CharField(max_length=200,db_column='wigosid')
	code = models.IntegerField(db_column='countrycode')
	area = models.CharField(max_length=200,db_column='countryarea')
	latitude = models.FloatField()
	longitude = models.FloatField()
	created = models.DateField()

	class Meta:
		managed=False
		db_table = 'volaex'

	def __str__(self):
		return "name: {} idx: {} subidx: {} created:{}".format(self.name,self.indexnbr,self.subindexnbr,self.created)


class Country(models.Model):
	code = models.CharField(db_column='cc',max_length=3,primary_key=True)
	name = models.CharField(max_length=50)
	_bounding_box = models.CharField(db_column='extent',max_length=5000)
	vola_code = models.IntegerField()

	class Meta:
		managed=False
		db_table = 'countrymetadata'


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
	year = models.IntegerField(db_column='yyyy')
	month = models.IntegerField(db_column='mm')
	day = models.IntegerField(db_column='dd')
	hour = models.IntegerField(db_column='hourperiod')
	center = models.CharField(max_length=10)
	filetype = models.CharField(max_length=5)
	date = models.DateField(db_column='mydate')


	class Meta:
		managed = False
		db_table = 'importsex'
		ordering = ['year','month','day','hour','center','filetype']

	def __str__(self):
		return "{}-{}-{}-{}-{}-{}".format(self.year,self.month,self.day,self.hour,self.center,self.filetype)

	def to_date(self):
		return date(self.year,self.month,self.day)

