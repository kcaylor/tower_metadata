from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from flask.ext.mongoengine import MongoEngine
from flask.ext.bower import Bower
from slacker import Slacker
from config import config
import os

# Initialize the flask extensions for this app:
slack = Slacker(os.environ.get('SLACK_TOKEN'))
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

    from app.models.metadata import Metadata

    # Set up the application routes:
    @app.route('/')
    def index():
        metadata = Metadata.objects().first()
        return render_template(
            'index.html',
            metadata=metadata)

    @app.route('/<int:year>/<int:doy>')
    def file_year_doy(year=2015, doy=1):
        metadata = Metadata.objects(
            year=year,
            doy=doy).first()
        if metadata is None:
            return render_template('404.html')
        else:
            return render_template(
                'file.html',
                metadata=metadata)

    @app.route('/<int:year>/<int:month>/<int:day>')
    def file_year_month_day(year=2015, month=1, day=20):
        from datetime import datetime
        date = datetime(year=year, month=month, day=day)
        metadata = Metadata.objects(
            date=date).first()
        if metadata is None:
            return render_template('404.html')
        else:
            return render_template(
                'file.html',
                metadata=metadata)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    # Put any template helper functions in here:
    @app.context_processor
    def helper_functions():

        def sig_fig(x=None, n=None):
            from math import floor, log10
            if n is not None:
                n = int(n)
            if x is None:
                return x
            if x == 0:
                return x
            if n <= 0:
                return x
            else:
                return round(x, -int(floor(log10(abs(x)))) + (n - 1))

        def label_pct(pct):
            if pct is None:
                return 'danger'
            if pct > 90:
                return 'success'
            if pct < 60:
                return 'danger'
            return 'warning'

        return dict(
            label_pct=label_pct,
            sig_fig=sig_fig
        )

    return app
