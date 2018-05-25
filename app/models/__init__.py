"""Initialize Tower Metadata models."""
from flask.ext.mongoengine import MongoEngine
from flask.ext.login import LoginManager
from settings import units

DATA_FILES = [
    'upper',        # Let's comment each of these...
    'Table1',       #
    'lws',          #
    'licor6262',    #
    'WVIA',         #
    'Manifold',     #
    'flux',         #
    'ts_data',      #
    'Table1Rain',   #  
    'unknown',      #  Removed on May 24, 2018 (folder does not exist on Dropbox)
]

non_static_attrs = ['source', 'program', 'logger']

static_attrs = ['station_name', 'lat', 'lon', 'elevation',
                'Year', 'Month', 'DOM', 'Minute', 'Hour',
                'Day_of_Year', 'Second', 'uSecond', 'WeekDay']

db = MongoEngine()
login_manager = LoginManager()


# Setting expected ranges for units.
flag_by_units = {}

for variable in units:
    for unit in units[variable]['units']:
        flag_by_units.update({
            unit: {
                'min': units[variable]['min'],
                'max': units[variable]['max']}
        })


from .metadata import Metadata, DropboxFiles
from .user import User
