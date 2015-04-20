from . import db


# Variables contained within Files:
class Variable(db.EmbeddedDocument):

    flags = db.ListField(db.StringField)
    name = db.StringField(db_field='var')
    units = db.StringField()
    count = db.IntField()
    avg_val = db.FloatField(db_field='mean')  # Avoid function names
    std_val = db.FloatField(db_field='std')
    min_val = db.FloatField(db_field='min')
    max_val = db.FloatField(db_field='max')
    p25th = db.FloatField(db_field='25%')
    p75th = db.FloatField(db_field='75%')
    content_type = db.StringField(db_field='content_coverage_type')
    coordinates = db.StringField()
    comment = db.StringField()


# Files contained within Metadata:
class File(db.EmbeddedDocument):

    source = db.StringField()
    instrument = db.StringField()
    filename = db.StringField()
    frequency = db.FloatField()

    # The File object contains a list of Variables:
    variables = db.EmbeddedDocumentListField(Variable)


# The Metadata object
class Metadata(db.Document):

    def __init__(self, netcdf=None):
        if netcdf is not None:
            # Parse the netcdf and initialize the metadata object
            print "Parsing the netcdf file to initialize Metadata"
        else:
            pass

    license = db.StringField()
    title = db.StringField()
    creator = db.StringField(db_field='creator_name', default='Kelly Caylor')
    creator_email = db.EmailField()
    institution = db.StringField()
    aknowledgements = db.StringField()
    feature_type = db.StringField(db_field='featureType')
    year = db.IntField(required=True)
    month = db.IntField(required=True)
    doy = db.IntField(required=True)
    date = db.DateTimeField(required=True)
    summary = db.StringField()
    conventions = db.StringField()
    naming_authority = db.StringField()  # or URLField?

    # The Metadata object contains a list of Files:
    files = db.EmbeddedDocumentListField(File)

    meta = {
        'collection': 'metadata',
        'ordering': ['-date'],
        'index_background': True,
        'indexes': [
            'year',
            'month',
            'doy',
        ]
    }

    def create_fake_metadata(*args, **kwargs):
        raise NotImplementedError
