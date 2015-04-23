# Read in all the app config settings stored in .env
# Do this before anything else!
import os
if os.path.exists('.env'):
        print('Importing environment from .env...')
        for line in open('.env'):
            var = line.strip().split('=')
            if len(var) == 2:
                os.environ[var[0]] = var[1]

# Import the ORM for the metadata
from mongoengine import connect
from app.models.metadata import Metadata, DropboxFiles

# Set the config settings to whatever the app is using.
from config import config
this_config = config[os.getenv('FLASK_CONFIG') or 'default']

# Make the database connection:
connect(host=this_config().mongo_url())

# Figure out what day it is:
from datetime import datetime
date = datetime.now()
year = date.year
doy = date.toordinal() - datetime(
    year=date.year,
    month=1,
    day=1).toordinal() + 1


# Check to see if we have this day already:
if Metadata.objects(year=year, doy=doy).first() is None:

    # Try to build the file:
    todays_metadata = Metadata(
        year=year,
        doy=doy,
        files=DropboxFiles.find_files(year=year, doy=doy)
    ).generate_metadata()

# Okay, we're done with today.
# Let's check the previous 6 days too, just in case:
for each_day in range(doy - 6, doy - 1):
    if Metadata.objects(year=year, doy=each_day).first() is None:
        # Try to build the file:
        todays_metadata = Metadata(
            year=year,
            doy=each_day,
            files=DropboxFiles.find_files(year=year, doy=each_day)
        ).generate_metadata()
