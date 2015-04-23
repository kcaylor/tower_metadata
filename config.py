import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('APP_SECRET')
    ROOT_DIR = os.environ.get('ROOT_DIR')

    @staticmethod
    def init_app(app):
        pass

    def mongo_url(self):

        if self.MONGODB_SETTINGS['username'] is '':
            return 'mongodb://' + self.MONGODB_SETTINGS['host'] + \
                ':' + str(self.MONGODB_SETTINGS['port']) + \
                '/' + self.MONGODB_SETTINGS['db']
        else:
            return 'mongodb://' + self.MONGODB_SETTINGS['username'] + \
                ':' + self.MONGODB_SETTINGS['password'] + \
                '@' + self.MONGODB_SETTINGS['host'] + \
                ':' + str(self.MONGODB_SETTINGS['port']) + \
                '/' + self.MONGODB_SETTINGS['db']


class TestingConfig(Config):
    TESTING = True
    MONGODB_SETTINGS = {
        "db": 'testing',
        "username": '',
        "password": '',
        "host": 'localhost',
        "port": 27017
    }


class DevelopmentConfig(Config):
    ROOT_DIR = os.environ.get('ROOT_DIR')
    DEBUG = True
    # MONGODB_DB = os.environ.get('MONGODB_DEV_DATABASE')
    # MONGODB_USERNAME = os.environ.get('MONGODB_DEV_USER')
    # MONGODB_PASSWORD = os.environ.get('MONGODB_DEV_PASSWORD')
    # MONGODB_HOST = os.environ.get('MONGODB_DEV_HOST')
    # MONGODB_PORT = int(os.environ.get('MONGODB_DEV_PORT'))
    MONGODB_SETTINGS = {
        "db": os.environ.get('MONGODB_DEV_DATABASE'),
        "username": os.environ.get('MONGODB_DEV_USER'),
        "password": os.environ.get('MONGODB_DEV_PASSWORD'),
        "host": os.environ.get('MONGODB_DEV_HOST'),
        "port": int(os.environ.get('MONGODB_DEV_PORT'))
    }

config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig,
    'testing': TestingConfig
}
