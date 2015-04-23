from __init__ import db, flag_by_units


# Variables contained within Files:
class Variable(db.DynamicEmbeddedDocument):

    flags = db.ListField(db.StringField())
    expected_count = db.IntField()
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

    def clean(self):
        # Get the flag_by_units dict.
        # check status of data and raise flags
        flags = []

        if self.expected_count * 11. / 12. < self.count < self.expected_count:
            flags.append('missing a little data')
        elif self.expected_count / 2. < self.count <= \
                self.expected_count * 11. / 12.:
            flags.append('missing some data')
        elif self.expected_count / 12. <= self.count <= \
                self.expected_count / 2.:
            flags.append('missing lots of data')
        elif self.count == 0:
            flags.append('no data')

        try:
            if self.name.startswith('del'):
                pass
            elif self.comment == 'Std':  # don't check std_dev
                pass
            else:
                if self.max_val > flag_by_units[self.units]['max']:
                    flags.append('contains high values')
                if self.min_val < flag_by_units[self.units]['min']:
                    flags.append('contains low values')
        except:
            pass
        self.flags = flags

    @staticmethod
    def generate_variable(var=None, ds=None, df=None, ts=None):
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
                count=df['count']
            )
        return this_var

    @staticmethod
    def generate_fake(n=7):
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
            expected_count=randint(1, 150)
        )
        return this_variable
