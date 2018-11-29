import datetime
import urllib
from django import template
from django.urls import reverse
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def make_class(periods,mydate,myperiod,mycenter,mytype):
    key = "{}-{:02d}-{}-{}".format(mydate.strftime("%Y-%m-%d"),myperiod,mycenter,mytype)
    print(mydate)
    return "imported" if key in periods else "empty"

@register.simple_tag
def make_link(periods,mydate,myperiod,mycenter,mytype):
    key = "{}-{:02d}-{}-{}".format(mydate.strftime("%Y-%m-%d"),myperiod,mycenter,mytype)
    if key in periods :
        #return reverse('filedownload',kwargs={'center' : mycenter , 'period' : myperiod , 'filetype' : mytype , 'date' : mydate.strftime('%Y%m%d')})
        kwargs={'center' : mycenter , 'period' : myperiod , 'filetype' : mytype , 'date' : mydate.strftime('%Y%m%d')}
        url=reverse('filedownload')
        url = "{}?{}".format(url,urllib.parse.urlencode(kwargs))
        mytype = "SYN" if mytype == 'SYNOP' else 'TMP' 
        return format_html("<a class='downloadlink' href='{}'>{}</a>",url,mytype)
    else:
        return ""
