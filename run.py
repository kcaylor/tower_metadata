import os
from flask import Flask
# from flask.ext.mongoengine import MongoEngine
# from mongoengine import connect
from pymongo import MongoClient
from waitress import serve
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment


# Function to create a mongodb uri from the app config settings.
def create_db_uri(config):
    return 'mongodb://' + config['MONGODB_SETTINGS']['username'] + \
        ':' + config['MONGODB_SETTINGS']['password'] + '@' + \
        config['MONGODB_SETTINGS']['host'] + ':' + \
        config['MONGODB_SETTINGS']['port'] + '/' + \
        config['MONGODB_SETTINGS']['db']

# Read in all the app config settings stored in .env
if os.path.exists('.env'):
        print('Importing environment from .env...')
        for line in open('.env'):
            var = line.strip().split('=')
            if len(var) == 2:
                os.environ[var[0]] = var[1]

from config import config

bootstrap = Bootstrap()
moment = Moment()

# Let's use the default config for now (usually is Development)
config_name = 'default'

# Do the stuff necessary to set up the Flask application
app = Flask(__name__)
app.config.from_object(config[config_name])
config[config_name].init_app(app)
bootstrap.init_app(app)
moment.init_app(app)

# Make the mongodb uri and establish a connection to the database:
db_uri = create_db_uri(app.config)
client = MongoClient(db_uri)
db = client.mpala_tower_metadata
Metadata = db.metadata

# attach routes and custom error pages here
from main import main as main_blueprint
app.register_blueprint(main_blueprint)

# Start up the app
port = int(os.getenv('PORT', 5000))
serve(app, port=port)
