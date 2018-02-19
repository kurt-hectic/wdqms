from django.conf import settings

def global_settings(request):
    # return any necessary values
    return {
        'OSCAR_STATION_REPORT': 'https://oscar.wmo.int/surface/index.html#/search/station/stationReportDetails/'
    }
