from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.mongoengine import MongoEngine
from flask.ext.bower import Bower

from config import config

# Initialize the flask extensions for this app:
bootstrap = Bootstrap()
bower = Bower()
moment = Moment()
db = MongoEngine()  # Warning: Must use pymongo 2.8 w/ mongoengine 0.7.1


def create_app(config_name):

    # Do the stuff necessary to set up the Flask application
    app = Flask(__name__)
    # Let's use the default config for now (set to Development):
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize the Flask extensions:
    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    bower.init_app(app)

    # Set up the application routes:
    @app.route('/')
    def index():
        from app.models.metadata import Metadata
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

    return app
