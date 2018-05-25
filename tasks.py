"""Celery tasks for tower app."""
from flask import Flask
from mongoengine import connect
from config import config
from celery import Celery
import datetime


"""Celery application code."""
import os
if os.path.exists('.env'):
    for line in open('.env'):
        var = line.strip().split('=')
        if len(var) == 2:
            os.environ[var[0]] = var[1]

# Make the database connection:
# Set the config settings to whatever the app is using.
this_config = os.getenv('FLASK_CONFIG') or 'default'
app = Flask(__name__)
app.config.from_object(config[this_config])
config[this_config].init_app(app)
host = config[this_config]().MONGODB_SETTINGS['HOST']
connect(
    db='pulsepod-restore',
    host=host
)

from app.models import Metadata, DropboxFiles

# Make the database connection:
# connect(host=this_config().mongo_url())
find_files = DropboxFiles.find_files

celery = Celery('mpala_tower')
celery.config_from_object("celery_settings")


def doy(date=None):
    """Return a DOY from a datetime object."""
    if not date:
        date = datetime.datetime.now()
    this_ordinal = date.toordinal()
    year_ordinal = datetime.datetime(date.year, 1, 1).toordinal()
    return this_ordinal - year_ordinal + 1


@celery.task(bind=True)
def create_metadata_task(self, year, doy):
    """Celery task to create metadata."""
    # Import the ORM for the metadata
    self.update_state(state='PROGESS')
    Metadata(
        year=year,
        doy=doy,
        files=find_files(year=year, doy=doy)
    ).generate_metadata()


@celery.task(bind=True)
def process_smap_data(self):
    """Update SMAP data and upload to FTP server."""
    self.update_state(state='PROGRESS')
