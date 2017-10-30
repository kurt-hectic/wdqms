from django.db import models 
from django.utils import timezone
from datetime import date


class Period(models.Model):
	year = models.IntegerField(db_column='yyyy')
	month = models.IntegerField(db_column='mm')
	day = models.IntegerField(db_column='dd')
	hour = models.IntegerField(db_column='hourperiod')
	center = models.CharField(max_length=10)
	filetype = models.CharField(max_length=5)


	class Meta:
		managed = False
		db_table = 'imports'
		ordering = ['year','month','day','hour','center','filetype']

	def __str__(self):
		return "{}-{}-{}-{}-{}-{}".format(self.year,self.month,self.day,self.hour,self.center,self.filetype)

	def to_date(self):
		return date(self.year,self.month,self.day)

