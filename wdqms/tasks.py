from __future__ import absolute_import, unicode_literals
from celery import task
from .models import Station
import pandas as pd
import calendar
import datetime 
import timeit
import json
import urllib.parse
from urllib.parse import quote
import numpy as np
from collections import namedtuple
import sys,csv,string,time
import re
from datetime import date
import datetime
from django.db import IntegrityError
from os import listdir
from os.path import isfile,join
import os
import gzip
import re,os,sys
import subprocess
import logging
from django.conf import settings
from wdqms.mytasks import NwpDownloadTask,FileDownloadTask,ImportStations







@task()
def task_number_one():
    stations = Station.objects.all()
    print("hello task %s" % len(stations))

@task()
def importStations():
    t = ImportStations()
    t.run()

@task()
def downloadFiles():
    t = FileDownloadTask()
    t.run()

@task()
def importNWP():
    t = NwpDownloadTask()    
    t.run()


