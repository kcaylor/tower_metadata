from __init__ import *


# Variables contained within Files:
class Variable(db.EmbeddedDocument):
    timestep_count = db.IntField()
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

    def generate_flags(self, flag_by_units):
        # check status of data and raise flags
        flags = []

        if self.timestep_count*11/12 < self.count < self.timestep_count:
            flags.append('missing a little data')
        elif self.timestep_count < self.count <= self.timestep_count*11/12:
            flags.append('missing some data')
        elif self.timestep_count/12 <= self.count <= self.timestep_count/2:
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
        return self

    def generate_variable(self, var, ds, df_summ, flag_by_units):
        if df_summ[var]['count'] != 0:
            self = Variable(
                name=var,
                timestep_count=len(ds['time']),
                count=df_summ[var]['count'],
                avg_val=df_summ[var]['mean'],
                std_val=df_summ[var]['std'],
                min_val=df_summ[var]['min'],
                p25th=df_summ[var]['25%'],
                p75th=df_summ[var]['75%'],
                max_val=df_summ[var]['max'],
                units=ds[var].attrs['units'],
                comment=ds[var].attrs['comment'],
                coordinates=ds[var].attrs['coordinates'],
                content_type=ds[var].attrs['content_coverage_type'],
            )
        else:
            self = Variable(
                name=var,
                timestep_count=len(ds['time']),
                count=df_summ[var]['count']
            )
        self.generate_flags(flag_by_units)

        return self

    @staticmethod
    def generate_fake(n=5):
        from random import choice, randint, random
        from faker import Faker
        fake = Faker()
        vals = [random() * 100 for i in range(1, 7)]
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
    datafile = db.StringField()  # upper, lws...
    filename = db.StringField()
    frequency = db.FloatField()
    frequency_flag = db.StringField()

    # The File object contains a list of Variables:
    variables = db.EmbeddedDocumentListField(Variable)

    def process_netcdf(self, input_dir, static_attrs):
        ds = xray.Dataset()
        ds = xray.open_dataset(join(input_dir, self.datafile, self.filename),
                               decode_cf=True, decode_times=True)
        df = ds.to_dataframe()

        # drop from df, columns that don't change with time
        exclude = [var for var in static_attrs if var in df.columns]
        df_var = df.drop(exclude, axis=1)  # dropping vars like lat, lon

        # get some descriptive statistics on each of the variables
        df_summ = df_var.describe()
        return ds, df_summ

    def programmed_frequency(self, input_dir):
        data = self.datafile
        program = self.source.split('CPU:')[1].split(',')[0]
        try:
            prog = open(join(input_dir, 'programs', program))
        except:
            self.frequency_flag = 'program: %s not found' % program
            self.frequency = float('nan')
            return self
        lines = prog.readlines()
        i = 0
        k = 0
        interval = None
        DT = 'DataTable'
        DI = 'DataInterval'
        CT = 'CallTable'
        for i in range(len(lines)):
            if lines[i].split()[0:] == [DT, data]:
                k = i
            if lines[i].split()[0:1] == DI and i <= (k+2):
                interval = lines[i].split(',')[1]
                units = lines[i].split(',')[2]
            i += 1
        if interval is None:
            i = 0
            for i in range(len(lines)):
                if lines[i].split()[0:1] == 'Scan':
                    interval = lines[i].split('(')[1].split(',')[0]
                    units = lines[i].split(',')[1]
                if lines[i].split()[0:2] == [CT, data] and i <= (k+7):
                    interval = interval
                    units = units
                else:
                    interval = None
                    units = None
                i += 1
        if interval is None:
            self.frequency_flag = 'could not find interval in %s' % program
            self.frequency = float('nan')
            return self
        try:
            num = int(interval)
        except:
            for line in lines:
                if line.startswith('Const '+interval):
                    a = line.split('=')[1]
                    b = a.split()[0]
                    num = int(b)
        self.frequency = convert_to_sec(num, units)
        self.frequency_flag = 'found frequency'

        return self

    def generate_file(self, input_dir, static_attrs, flag_by_units):
        ds, df_summ = self.process_netcdf(input_dir, static_attrs)
        self.source = ds.attrs['source']
        self.instrument = ds.attrs['instrument']
        this_var = Variable()
        for var in df_summ:
            self.variables.append(this_var.generate_variable(var, ds,
                                                             df_summ,
                                                             flag_by_units))
        self.programmed_frequency(input_dir)
        return self

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

    def find_files(self, input_dir, datas):
        f = 'raw_MpalaTower_%i_%03d.nc' % (self.year, self.doy)
        for data in datas:
            if f in os.listdir(join(input_dir, data)):
                this_file = File(filename=f, datafile=data)
                self.files.append(this_file)
        return self

    def generate_metadata(self, input_dir, static_attrs):
        ds, df_summ = self.files[0].process_netcdf(input_dir, static_attrs)

        self.license = ds.attrs['license']
        self.title = ds.attrs['title']
        self.creator = ds.attrs['creator_name']
        self.creator_email = ds.attrs['creator_email']
        self.institution = ds.attrs['institution']
        self.aknowledgements = ds.attrs['acknowledgement']
        self.feature_type = ds.attrs['featureType']
        self.summary = ds.attrs['summary']
        self.conventions = ds.attrs['Conventions']
        self.naming_authority = ds.attrs['naming_authority']

        return self

    def parse_netcdf(self, input_dir, datas, static_attrs, flag_by_units):
        self.find_files(input_dir, datas)
        self.generate_metadata(input_dir, static_attrs)
        for f in self.files:
            f.generate_file(input_dir, static_attrs, flag_by_units)
        self.save()

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
