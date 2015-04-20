from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.mongoengine import MongoEngine

# Read in all the app config settings stored in .env
# Do this before anything else!
import os
if os.path.exists('.env'):
        print('Importing environment from .env...')
        for line in open('.env'):
            var = line.strip().split('=')
            if len(var) == 2:
                os.environ[var[0]] = var[1]

# Now that we have the environmental variables loaded,
# let's import the configuration settings:
from config import config

# Initialize the flask extensions for this app:
bootstrap = Bootstrap()
moment = Moment()
db = MongoEngine()  # Warning: Must use pymongo 2.8 w/ mongoengine 0.7.1

# Do the stuff necessary to set up the Flask application
app = Flask(__name__)
# Let's use the default config for now (set to Development):
config_name = 'default'
app.config.from_object(config[config_name])
config[config_name].init_app(app)

# Initialize the Flask extensions:
bootstrap.init_app(app)
moment.init_app(app)
db.init_app(app)

# Import the ORM for the metadata
from models.metadata import Metadata, Variable, File


# Set up the application routes:
@app.route('/')
def index():
    metadata = Metadata.objects().first()
    return render_template(
        'index.html',
        metadata=metadata)


# Put any template helper functions in here:
@app.context_processor
def helper_functions():

    def label_pct(pct):
        if pct is None:
            return 'danger'
        if pct > 90:
            return 'success'
        if pct < 60:
            return 'danger'
        return 'warning'

    return dict(
        label_pct=label_pct
    )


# Start up the app:
from waitress import serve
port = int(os.getenv('PORT', 5000))
serve(app, port=port)
