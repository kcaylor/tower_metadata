
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
from app.models import db
from app.models.metadata import Metadata, DropboxFiles
from app.models.variable import Variable
from app.models.file import File
from app import create_app

from flask.ext.script import Manager, Shell


app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(
        app=app,
        db=db,
        Metadata=Metadata,
        DropboxFiles=DropboxFiles,
        Flie=File,
        Variable=Variable
    )

manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
def reset():
    """Reset the testing database"""
    if app.testing:
        print "Reseting testing database"
        print "\t...dropping old collections"
        Metadata.drop_collection()
        print "\t...generating new fake metadata"
        Metadata.generate_fake(10)
    else:
        print "Cannot run this command under %s config" % \
            app.config['FLASK_CONFIG']


@manager.command
def serve():
    """Starts the app (using waitress)"""
    from waitress import serve
    port = int(os.getenv('PORT', 5000))
    serve(app, port=port)

if __name__ == '__main__':
    manager.run()
