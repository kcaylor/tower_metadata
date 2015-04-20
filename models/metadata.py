from . import db


# Variables contained within Files:
class Variable(db.EmbeddedDocument):

    flags = db.ListField(db.StringField())
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

    @staticmethod
    def generate_fake(n=5):
        from random import choice, randint, random
        from faker import Faker
        fake = Faker()
        vals = [random() * 100 for i in [1, 2, 3, 4, 5, 6, 7]]
        vals.sort()
        this_variable = Variable(
            flags=fake.words(5),
            name=fake.name(),
            units=fake.word(),
            count=randint(1, 150),
            avg_val=sum(vals) / len(vals),
            std_val=choice(vals),
            min_val=min(vals),
            max_val=max(vals),
            p25th=vals[1],
            p75th=vals[-2],
            content_type=fake.words(2),
            coordinates=fake.words(3),
            comment=fake.sentence()
        )
        return this_variable


# Files contained within Metadata:
class File(db.EmbeddedDocument):

    source = db.StringField()
    instrument = db.StringField()
    filename = db.StringField()
    frequency = db.FloatField()

    # The File object contains a list of Variables:
    variables = db.EmbeddedDocumentListField(Variable)

    @staticmethod
    def generate_fake():
        from random import choice
        from faker import Faker
        fake = Faker()
        this_file = File(
            source=fake.word(),
            instrument=fake.word(),
            filename=fake.word(),
            frequency=choice([.1, 60, 600, 1800]),
            variables=[Variable.generate_fake() for i in range(1, 10)]
        )
        return this_file


# The Metadata object
class Metadata(db.Document):

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

    def parse_netcdf(self, netcdf=None):
        if netcdf is not None:
            # Parse the netcdf and initialize the metadata object
            print "Parsing the netcdf file to initialize Metadata"
        else:
            pass

    @staticmethod
    def generate_fake():
        from random import choice, randint
        from faker import Faker
        fake = Faker()
        this_metadata = Metadata(
            license=fake.word(),
            title=fake.sentence(),
            creator=fake.name(),
            creator_email=fake.email(),
            institution=fake.company(),
            aknowledgements=fake.sentence(),
            feature_type=fake.word(),
            year=fake.year(),
            month=fake.month(),
            doy=randint(1, 365),
            date=fake.date_time_this_month(),
            summary=fake.sentence(),
            conventions=fake.word(),
            naming_authority=fake.company(),
            files=[File.generate_fake() for i in range(1, 5)]
        )
        return this_metadata
