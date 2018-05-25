#!/usr/bin/python
# Read in all the app config settings stored in .env
# Do this before anything else!
import os
if os.path.exists('.env'):
        print('Importing environment from .env...')
        for line in open('.env'):
            var = line.strip().split('=')
            if len(var) == 2:
                os.environ[var[0]] = var[1]

import argparse
from datetime import datetime
# Import the ORM for the metadata
from mongoengine import connect
from app.models.metadata import Metadata, DropboxFiles
from config import config

# Figure out what day it is:
date = datetime.now()
year = date.year
doy = date.toordinal() - datetime(
    year=date.year,
    month=1,
    day=1).toordinal() + 1

today = 'YEAR: ' + str(year) + ', DOY:' + str(doy)
parser = argparse.ArgumentParser(
    description='Process Mpala Tower metadata.',
    epilog='NOTE: If YEAR or DOY are not provided, we use today, ' + today)
parser.add_argument('-f', '--force', action='store_true',
                    help='force rebuilding of the metadata')
parser.add_argument('-w', '--week', action='store_true',
                    help='check for previous 7 days')
parser.add_argument(
    '-y', '--year', metavar='YEAR', type=int, nargs='?',
    help='The year of the data you with to process (default: {YEAR})'.format(
        YEAR=year)
)
parser.add_argument(
    '-d', '--doy', metavar='DOY', type=int, nargs='?',
    help='The day of the year of the data to process (default: {DOY})'.format(
        DOY=doy)
)
parser.add_argument('--dropbox', action='store_true',
                    help='pull files from our dropbox backup')
parser.add_argument(
    '-n', '--next', metavar='NEXT', type=int, nargs='?',
    help='Parse the next N days, starting with the current YEAR, DOY')

args = parser.parse_args()

if args.year:
    year = args.year
if args.doy:
    doy = args.doy

print "Parsing metdata for Year:{year}, DOY:{doy}".format(
    year=year, doy=doy)

# Set the config settings to whatever the app is using.
this_config = config[os.getenv('FLASK_CONFIG') or 'default']

# Make the database connection:
connect(host=this_config.MONGODB_SETTINGS['HOST'])

# Specify which find_files function to use:
if args.dropbox:
    find_files = DropboxFiles.find_files
else:
    find_files = Metadata.find_files

# Check to see if we have this day already:
if Metadata.objects(year=year, doy=doy).first() is None:
    # Try to build the file:
    todays_metadata = Metadata(
        year=year,
        doy=doy,
        files=find_files(year=year, doy=doy)
    ).generate_metadata()
elif args.force:
    print "Forcing rebuild for Year:{year}, DOY:{doy}".format(
        year=year, doy=doy)
    current_metadata = Metadata.objects(year=year, doy=doy)
    for metadata in current_metadata:
        metadata.delete()
    todays_metadata = Metadata(
        year=year,
        doy=doy,
        files=find_files(year=year, doy=doy)
    ).generate_metadata()
else:
    print "Metadata already exists for Year:{year}, doy:{doy}".format(
        year=year, doy=doy)

if args.next:
    for day in range(doy + 1, doy + args.next):
        if Metadata.objects(year=year, doy=day).first() is None:
                # Try to build the file:
                print "Building metadata for YEAR:{year}, DOY:{doy}".format(
                    year=year, doy=day)
                todays_metadata = Metadata(
                    year=year,
                    doy=day,
                    files=find_files(year=year, doy=day)
                ).generate_metadata()
        elif args.force:
            print "Forcing rebuild for YEAR:{year}, DOY:{doy}".format(
                year=year, doy=day)
            current_metadata = Metadata.objects(
                year=year, doy=day)
            for metadata in current_metadata:
                metadata.delete()
            todays_metadata = Metadata(
                year=year,
                doy=day,
                files=find_files(
                    year=year, doy=day)
            ).generate_metadata()
        else:
            print "Metadata for YEAR:{year}, DOY:{doy} already exists".format(
                year=year, doy=day)

if args.week:
    if doy >= 7:
        print "Building 6 days of metadata, DOY:{start} to DOY:{end}".format(
            start=doy - 6, end=doy - 1)
        # Okay, we're done with today.
        # Let's check the previous 6 days too, just in case:
        for each_day in range(doy - 6, doy):
            if Metadata.objects(year=year, doy=each_day).first() is None:
                # Try to build the file:
                print "Building metadata for YEAR:{year}, DOY:{doy}".format(
                    year=year, doy=each_day)
                todays_metadata = Metadata(
                    year=year,
                    doy=each_day,
                    files=find_files(year=year, doy=each_day)
                ).generate_metadata()
            elif args.force:
                print "Forcing rebuild for YEAR:{year}, DOY:{doy}".format(
                    year=year, doy=each_day)
                current_metadata = Metadata.objects(
                    year=year, doy=each_day)
                for metadata in current_metadata:
                    metadata.delete()
                todays_metadata = Metadata(
                    year=year,
                    doy=each_day,
                    files=find_files(
                        year=year, doy=each_day)
                ).generate_metadata()
            else:
                print "Metadata for YEAR:{year}, DOY:{doy} exists".format(
                    year=year, doy=each_day)
    else:
        print "Cannot build prior week for DOY less than 7"
