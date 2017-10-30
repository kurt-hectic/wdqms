import datetime
from django import template

register = template.Library()

@register.simple_tag
def make_class(periods,mydate,myperiod,mycenter,mytype):
	key = mydate.strftime("%Y-%-m-%-d") + "-{}-{}-{}".format(myperiod,mycenter,mytype)
	return "imported" if key in periods else "empty"
