from flask.ext.mongoengine import MongoEngine

db = MongoEngine()
db.connect(host='mongodb://joey:joejoe@dogen.mongohq.com:10097/mpala_tower_metadata')

import pandas as pd
import datetime as dt
import numpy as np
import os
import xray
from posixpath import join

ROOTDIR = 'C:/Users/Julia/Documents/GitHub/MpalaTower/raw_netcdf_output/'
datas = ['upper', 'Table1', 'lws', 'licor6262', 'WVIA',
         'Manifold', 'flux', 'ts_data', 'Table1Rain']
non_static_attrs = ['instrument', 'source', 'program', 'logger']
static_attrs = ['station_name', 'lat', 'lon', 'elevation',
                'Year', 'Month', 'DOM', 'Minute', 'Hour',
                'Day_of_Year', 'Second', 'uSecond', 'WeekDay']

# Setting expected ranges for units. It is ok to include multiple ways of
# writing the same unit, just put all the units in a list
flag_by_units = {}

temp_min = 0
temp_max = 40
temp = ['Deg C', 'C']
for unit in temp:
    flag_by_units.update({unit: {'min': temp_min, 'max': temp_max}})

percent_min = 0
percent_max = 100
percent = ['percent', '%']
for unit in percent:
    flag_by_units.update({unit: {'min': percent_min, 'max': percent_max}})

shf_min = ''
shf_max = ''
shf = ['W/m^2']

shf_cal_min = ''
shf_cal_max = ''
shf_cal = ['W/(m^2 mV)']

batt_min = 11
batt_max = 240
batt = ['Volts', 'V']
for unit in batt:
    flag_by_units.update({unit: {'min': batt_min, 'max': batt_max}})

PA_min = 15
PA_max = 25
PA = ['uSec']


def convert_to_sec(num, units):
    if units.startswith(('Min', 'min')):
        out = int(num)*60
    elif units.startswith(('ms', 'mS')):
        out = float(num)/1000
    elif units.startswith(('s', 'S')):
        out = int(num)
    else:
        print('couldn\'t parse units')
        return (num, units)
    return out
