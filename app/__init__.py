"""Create the Tower_Metadata application."""
from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
# from flask.ext.mailgun import Mailgun
from flask.ext.wtf import CsrfProtect
from flask.ext.bower import Bower
from config import config
from pymongo import ReadPreference
from app.models import db, login_manager

# Initialize the flask extensions for this app:
# slack = Slacker(os.environ.get('SLACK_TOKEN'))
bootstrap = Bootstrap()
bower = Bower()
moment = Moment()
csrf = CsrfProtect()
# mail = Mailgun()


login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
login_manager.login_message = \
    'Give your data a pulse by logging in or signing up!'
login_manager.login_message_category = "info"


def create_app(config_name):
    """Create the tower_metadata application for deployment."""
    # Do the stuff necessary to set up the Flask application
    app = Flask(__name__)
    # Let's use the default config for now (set to Development):
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # Initialize the Flask extensions:
    bootstrap.init_app(app)
    moment.init_app(app)
    bower.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)

    from mongoengine import connect
    host = config[config_name]().MONGODB_SETTINGS['HOST']
    connect(
        db='pulsepod-restore',  # Not needed because db is in the host uri, or maybe not.
        host=host
    )
    if config_name is 'testing':
        db.init_app(app)
        db.read_preference = ReadPreference.PRIMARY_PREFERRED
    # attach routes and custom error pages here
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # from .auth import auth as auth_blueprint
    # app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .ajax import ajax as ajax_blueprint
    app.register_blueprint(ajax_blueprint, url_prefix='/ajax')

    # @app.route('/thisweek')
    # def this_week():
    #     from datetime import datetime
    #     date = datetime.now()
    #     # Find the Metadata from the past week.

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

        def min_ok(min_ok):
            if min_ok:
                return 'default'
            else:
                return 'danger'

        def max_ok(max_ok):
            if max_ok:
                return 'default'
            else:
                return 'danger'

        return dict(
            label_pct=label_pct,
            sig_fig=sig_fig,
            min_ok=min_ok,
            max_ok=max_ok
        )

    return app
