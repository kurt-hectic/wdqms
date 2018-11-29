"""wdqms URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include,url
from django.contrib import admin
from django.views.generic.base import RedirectView
from django.core.urlresolvers import reverse_lazy


from . import views 

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index, name='index'),
    url(r'^listspace$', views.listspace, name='listspace'),
    url(r'^listimports-json', views.listimports_json, name='listimports_json'),
    url(r'^listimports$', views.listimports, name='listimports'),
    url(r'^map$', views.map, name='map'),
    url(r'^map/(?P<filetype>[^/]+)/(?P<center>[^/]+)/(?P<date>[^/]+)/(?P<hour>[^/]+)$', views.map, name='map_date'),
    url(r'^maxmap$', views.maxmap, name='maxmap'),
    url(r'^map.html', RedirectView.as_view(url=reverse_lazy('map'))),
    url(r'^avsbmap$', views.avsbmap, name='avsbmap'),
    url(r'^country_cal', views.country_cal, name='country_cal'),
    url(r'^country_dt', views.country_dt, name='country_dt'),
    url(r'^country$', views.country, name='country'),
    url(r'^country/(?P<country>[^/]+)$', views.country, name='country_with_name'),
    url(r'^data$', views.data, name='data'),
    url(r'^availability-report$', views.availability_report, name='availability_report'),
    url(r'^station/(?P<stationid>[^/]+)$', views.station, name='station'),
    url(r'^station/$', views.station, name='station'),
    url(r'^country_dashboard/(?P<country>[^/]+)$', views.dashboard, name='dashboard'),
    url(r'^country_dashboard$', views.dashboard, name='dashboard'),
    url(r'^api/observations_agg/(?P<center>[^/]+)/(?P<date>[^/]+)/(?P<hour>[^/]+)/(?P<variable>[^/]+)$', views.observations_agg, name='observations_agg' ),
    url(r'^api/nrreceived/(?P<stationid>[^/]+)/(?P<variable>[^/]+)', views.nrreceived, name='nrreceived' ),
    url(r'^api/countryaggregate/(?P<countrycode>[^/]+)', views.countryaggregate, name='countryaggregate' ),
    url(r'^api/download_file$', views.download_file, name='filedownload' ),
    url(r'^listimports.php$', RedirectView.as_view(url='listimports'), name='legacy-listimports' ),
    url(r'^map.php$', RedirectView.as_view(url='map'), name='legacy-map' ),
    url(r'^country.php$', RedirectView.as_view(url='country'), name='legacy-country' ),
    url(r'^listspace.php$', RedirectView.as_view(url='listspace'), name='legacy-listspace' ),
    url(r'^availability-report.php$', RedirectView.as_view(url='availability-report'), name='legacy-availability-report' ),
]
