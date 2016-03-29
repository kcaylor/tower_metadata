"""Variable Definitions from Mpala Tower Data to be used in Metadata."""
from . import db, flag_by_units
from . import DATA_FILES

VARIABLE_CONTEXTS = [
    'Soil',
    'Air',
    'Upwelling',
    'Downwelling',
    'Surface',
    ''
]


# Variables contained within Files:
class Variable(db.DynamicEmbeddedDocument):
    """Definition of Variable class to be used in MongoEngine."""

    expected_count = db.IntField()
    context = db.StringField(choices=VARIABLE_CONTEXTS, default='')
    filename = db.StringField(choices=DATA_FILES, default='unknown')
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
    comment = db.StringField()

    # QA/QC stuff for this variable
    status = db.StringField()
    pct_data = db.FloatField()
    min_ok = db.BooleanField()
    max_ok = db.BooleanField()
    flags = db.ListField(db.StringField())

    # Clean automagically gets called by mongoengine whenever a
    # variable is written to the db. Therefore, we put all our QA/QC
    # code into clean()
    def clean(self):
        """QA/QC Methods for variables."""
        # Get the flag_by_units dict.
        # check status of data and raise flags
        flags = []
        status = 'success'  # Default status is ok (green)
        min_ok = True  # Assume that values are in range for min
        max_ok = True  # Assume that values are in range for max

        # If we have about 92% of the data, then just mention it
        if self.expected_count * 11. / 12. < self.count < self.expected_count:
            flags.append('missing a little data')
            status = 'info'
        # If we have more than 50% of the data, then warn us
        elif self.expected_count / 2. < self.count <= \
                self.expected_count * 11. / 12.:
            flags.append('missing some data')
            status = 'warning'
        # If we don't even have 50%, then there's a problem
        elif self.count <= self.expected_count / 2.:
            flags.append('missing lots of data')
            status = 'danger'
        # If there's no data at all, then go grey.
        elif self.count == 0:
            flags.append('contains no data')
            status = 'default'
        # Check on variable min/max, specified by units
        try:
            # TODO: Check flag_by_variable_name for this variable.
            if self.name.startswith('del'):
                pass
            elif self.comment == 'Std':  # don't check std_dev
                pass
            else:
                # Check to see if these units are within acceptable ranges:
                if self.max_val > flag_by_units[self.units]['max']:
                    flags.append('contains high values')
                    status = 'info'
                    max_ok = False
                if self.min_val < flag_by_units[self.units]['min']:
                    flags.append('contains low values')
                    status = 'info'
                    min_ok = False
        except:
            pass
        # Watch out for divide by zero stuff
        if self.expected_count > 0:
            self.pct_data = round(self.count / self.expected_count * 100)
        else:
            self.pct_data = 0
        # Now assign the qa/qc variables
        self.min_ok = min_ok
        self.max_ok = max_ok
        self.status = status
        self.flags = flags

    @staticmethod
    def generate_variable(var=None, ds=None, df=None, ts=None):
        """Create a Variable object."""
        if df['count'] != 0:
            this_var = Variable(
                name=var,
                expected_count=ts,
                count=df['count'],
                avg_val=df['mean'],
                std_val=df['std'],
                min_val=df['min'],
                p25th=df['25%'],
                p75th=df['75%'],
                max_val=df['max'],
                units=ds.attrs['units'],
                comment=ds.attrs['comment'],
                content_type=ds.attrs['content_coverage_type'],
            )
        else:
            this_var = Variable(
                name=var,
                expected_count=ts,
                count=df['count'],
                min_ok=1,
                max_ok=1,
                pct_data=0,
            )
        return this_var

    @staticmethod
    def generate_fake(n=7):
        """Create a fake Variable object for use in testing and development."""
        from random import choice, randint, random
        from faker import Faker
        fake = Faker()
        vals = [random() * 100 for i in range(1, n)]
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
            content_type=fake.word(),
            coordinates=fake.word(),
            comment=fake.sentence(),
            expected_count=randint(1, 150),
            max_ok=random() < 0.5,
            min_ok=random() < 0.5,
            pct_data=round(random() * 100)
        )
        return this_variable
