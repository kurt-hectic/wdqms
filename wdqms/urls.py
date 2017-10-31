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
from . import views 

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index, name='index'),
    url(r'^listspace$', views.listspace, name='listspace'),
    url(r'^listimports-json', views.listimports_json, name='listimports_json'),
    url(r'^listimports$', views.listimports, name='listimports'),
    url(r'^map$', views.map, name='map'),
    url(r'^map.html', views.map, name='map'),
    url(r'^country_cal', views.country_cal, name='country_cal'),
    url(r'^country_dt', views.country_dt, name='country_dt'),
    url(r'^country$', views.country, name='country'),
    url(r'^data$', views.data, name='data'),

    url(r'^listimports.php$', RedirectView.as_view(url='listimports'), name='legacy-listimports' ),
    url(r'^map.php$', RedirectView.as_view(url='map'), name='legacy-map' ),
    url(r'^country.php$', RedirectView.as_view(url='country'), name='legacy-country' ),

]
