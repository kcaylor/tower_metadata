from . import db
from .variable import Variable
import xray


def convert_to_sec(num, units):
    if units.startswith(('Min', 'min')):
        out = int(num) * 60
    elif units.startswith(('ms', 'mS')):
        out = float(num) / 1000
    elif units.startswith(('s', 'S')):
        out = int(num)
    else:
        print('couldn\'t parse units')
        return (num, units)
    return out


# Files contained within Metadata:
class File(db.DynamicEmbeddedDocument):

    DATA_FILES = [
        'upper',        # Let's comment each of these...
        'Table1',       #
        'lws',          #
        'licor6262',    #
        'WVIA',         #
        'Manifold',     #
        'flux',         #
        'ts_data',      #
        'Table1Rain'    #
    ]

    source = db.StringField()
    instrument = db.StringField()
    datafile = db.StringField(
        choices=DATA_FILES
    )
    filename = db.StringField()
    frequency = db.FloatField()
    frequency_flag = db.StringField()
    timestep_count = db.IntField()
    date = db.DateTimeField()

    # Where to find the datalogger output for this file.
    # We read this file to find and analyze variables.
    file_location = db.StringField()

    # The File object contains a list of Variables:
    variables = db.EmbeddedDocumentListField(Variable)

    def get_program_location(self):
        # Program locations should always be taken from dropbox.
        # So we need to edit this.
        from posixpath import join
        program = self.source.split('CPU:')[1].split(',')[0]
        return join(self.input_dir, 'programs', program)

    @staticmethod
    def get_programmed_frequency(program=None, datafile=None):
        try:
            prog = open(program)
        except:
            frequency_flag = 'program: %s not found' % program
            frequency = float('nan')
            timestep_count = float('nan')
            return [frequency, frequency_flag, timestep_count]
        lines = prog.readlines()
        i = 0
        k = 0
        interval = None
        dt = 'DataTable'
        di = 'DataInterval'
        ct = 'CallTable'
        for i in range(len(lines)):
            if lines[i].split()[0:] == [dt, datafile]:
                k = i
            if lines[i].split()[0:1] == di and i <= (k + 2):
                interval = lines[i].split(',')[1]
                units = lines[i].split(',')[2]
            i += 1
        if interval is None:
            i = 0
            for i in range(len(lines)):
                if lines[i].split()[0:1] == 'Scan':
                    interval = lines[i].split('(')[1].split(',')[0]
                    units = lines[i].split(',')[1]
                if lines[i].split()[0:2] == [ct, datafile] \
                        and i <= (k + 7):
                    interval = interval
                    units = units
                else:
                    interval = None
                    units = None
                i += 1
        if interval is None:
            frequency_flag = 'could not find interval in %s' % program
            frequency = float('nan')
            timestep_count = float('nan')
            return [frequency, frequency_flag, timestep_count]
        try:
            num = int(interval)
        except:
            for line in lines:
                if line.startswith('Const ' + interval):
                    a = line.split('=')[1]
                    b = a.split()[0]
                    num = int(b)
        frequency = convert_to_sec(num, units)
        timestep_count = 24. * 60. * 60. / frequency
        frequency_flag = 'found frequency'
        return [frequency, frequency_flag, timestep_count]

    @staticmethod
    def process_netcdf(netcdf=None):
        from . import static_attrs
        ds = xray.Dataset()
        ds = xray.open_dataset(
            netcdf,
            decode_cf=True,
            decode_times=True
        )
        df = ds.to_dataframe()

        # drop from df, columns that don't change with time
        exclude = [var for var in static_attrs if var in df.columns]
        df_var = df.drop(exclude, axis=1)  # dropping vars like lat, lon

        # get some descriptive statistics on each of the variables
        df_summ = df_var.describe()
        return ds, df_summ

    def parse(self):
        ds, df_summ = self.process_netcdf(netcdf=self.filename)
        self.source = ds.attrs['source']
        self.instrument = ds.attrs['instrument']
        [
            self.frequency,
            self.frequency_flag,
            self.timestep_count
        ] = self.get_programmed_frequency(
            program=self.get_program_location(),
            datafile=self.datafile
        )
        for var in df_summ:
            self.variables.append(
                Variable.generate_variable(
                    var=var,
                    ds=ds[var],
                    df=df_summ[var],
                    ts=self.timestep_count
                )
            )
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
