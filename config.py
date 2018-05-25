"""Configuration for tower app."""
import os

basedir = os.path.abspath(os.path.dirname(__file__))


def make_mongo_uri(
        host='localhost',
        port=27017,
        database='default',
        replica_set=None,
        username=None,
        password=None):
    """Make the mongo connection URI."""
    uri = 'mongodb://'
    if username is not None and password is not None:
        uri += username + ':' + password + '@'
    if ',' in host:
        host = host.split(',')
    if not isinstance(host, basestring):
        if port is not None:
            host = [x + ':' + str(port) for x in host]
        uri += ",".join(host)
    else:
        uri += host
        if port is not None:
            uri += ':' + str(port)
    if database is not None:
        uri += '/' + database
    if replica_set is not None:
        uri += '?replicaSet=' + replica_set
    uri += '?ssl=true'
    return uri


class Config:
    """Configuration class for tower app."""

    SECRET_KEY = os.environ.get('APP_SECRET')
    ROOT_DIR = os.environ.get('ROOT_DIR')
    SLACK_TOKEN = os.environ.get('SLACK_TOKEN')
    
    @staticmethod
    def init_app(app):
        """Initialize the config."""
        pass


class TestingConfig(Config):
    """Test configuration settings."""

    TESTING = True
    SERVER_NAME = '0.0.0.0:5000'
    MONGODB_SETTINGS = {
        "db": 'testing',
        "username": '',
        "password": '',
        "host": 'localhost',
        "port": 27017
    }


class DevelopmentConfig(Config):
    """Development configuration settings."""

    ROOT_DIR = os.environ.get('ROOT_DIR')
    SERVER_NAME = 'mpala.herokuapp.com'
    DEBUG = True
    MONGODB_SETTINGS = {
        "HOST": make_mongo_uri(
            host=os.environ.get('MONGODB_DEV_HOST'),
            port=int(os.environ.get('MONGODB_DEV_PORT')),
            database=os.environ.get('MONGODB_DEV_DATABASE'),
            username=os.environ.get('MONGODB_DEV_USER'),
            password=os.environ.get('MONGODB_DEV_PASSWORD'),
            #replica_set=os.environ.get('MONGODB_DEV_REPLICASET')
        )
    }

config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig,
    'testing': TestingConfig
}
