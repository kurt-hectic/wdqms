from django.test import TestCase, override_settings
from wdqms.models import Observation,NrObservation
from wdqms.tasks import importNWP,importStations


@override_settings(WDQMS={
    'IMPORTER' : { 'PATH' : 'wdqms/testdata' , 'ENABLED_NWP_CENTERS' : ['JMA'] } , 
    'DATADIRS': { 'ECMWF' : 'dissemination.ecmwf.int/ECMF/', 'DWD' : "DWD/", 'JMA' : "qc.kishou.go.jp/WIGOS_QM/", 'NCEP' : "www.emc.ncep.noaa.gov/mmab/WIGOS" }}
    ,
    URL_OSCAR_STATIONS = 'wdqms/testdata/oscar-pressure-stations.json', URL_OSCAR_SCHEDULES = 'wdqms/testdata/surface_pressure_schedules_report-20181001.zip'
)
class ObservationTestCase(TestCase):
    fixtures = ['country']

    def setUp(self):
        importStations() 
        importNWP()

    def test_the_test(self):
        self.assertEqual("one", "one")
        self.assertEqual("one", "two")


    # To test... calendar API, filedownload , 
    # to test... removal of period cascades
    # import something that has been imported already
    # different centers
    # different SYNOP and TEMP
    # check: correct aggregation, creation of empty stations, duplicate marking, unknown stations
    # check about station.. correct schedules, diff mechanism works ok (do not add new stations when same.. , mark station as closed, re-open it by inserting new)
