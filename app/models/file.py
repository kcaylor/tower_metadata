"""File Class Definition for Mpala Tower Metadata."""
from . import db, DATA_FILES
from variable import Variable
import xarray
import requests

program_location = 'programs'

def convert_to_sec(num, units):
    """Convert time units to seconds."""
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
    """File object model defined for use in MongoEngine."""

    source = db.StringField()
    logger = db.StringField()
    datafile = db.StringField(
        # choices=DATA_FILES
    )
    filename = db.StringField()
    frequency = db.FloatField()
    frequency_flag = db.StringField()
    timestep_count = db.IntField()
    date = db.DateTimeField()
    program_name = db.StringField()
    program_location = db.StringField()

    # Where to find the datalogger output for this file.
    # We read this file to find and analyze variables.
    file_location = db.StringField()

    # The File object contains a list of Variables:
    variables = db.EmbeddedDocumentListField(Variable)

    def get_program(self):
        """Retrieve a program file from the Mpala Tower Dropbox listings."""
        # Must use Dropbox to get program files.
        from dropbox import Dropbox
        from posixpath import join
        import os

        # Set up the Dropbox connection. Not sure how access_tokens will work
        access_token = os.environ.get('access_token')
        dropbox_dir = os.environ.get('dropbox_dir')
        client = Dropbox(access_token)

        # If this is our first time with this file, set the program name and
        # location.
        self.program_location = join(
            dropbox_dir,
            program_location,
            self.program_name
        )
        # Retrieve the REST object from Dropbox
        prog_link = client.files_get_temporary_link(self.program_location)
        response = requests.get(prog_link.link)
        # Put the program file contents into an array for parsing
        program_content = response.text
        # Send that stuff back.
        return program_content

    @staticmethod
    def get_programmed_frequency(program_content=None, datafile=None):
        """Determine the frequency of data collection from the program file."""
        lines = program_content
        i = 0
        k = 0
        interval = None
        dt = 'DataTable'
        di = 'DataInterval'
        ct = 'CallTable'
        for i in range(len(lines)):
            line = lines[i].lstrip()
            if line.startswith(dt) and datafile in line:
                k = i
            if line.startswith(di) and i <= (k + 2):
                interval = line.split(',')[1]
                units = line.split(',')[2]
            i += 1
        if interval is None:
            i = 0
            for i in range(len(lines)):
                line = lines[i].lstrip()
                if line.startswith('Scan'):
                    interval_temp = line.split('(')[1].split(',')[0]
                    units_temp = line.split(',')[1]
                    k = i
                if line.startswith(ct) and datafile in line and i <= (k + 7):
                    interval = interval_temp
                    units = units_temp
                i += 1
        if interval is None:
            frequency_flag = 'could not find program interval'
            frequency = float('nan')
            timestep_count = int(0)
            return [frequency, frequency_flag, timestep_count]
        try:
            num = int(interval)
        except:
            for l in lines:
                line = l.lstrip()
                if line.startswith('Const ' + interval):
                    a = line.split('=')[1]
                    b = a.split()[0]
                    num = int(b)
        frequency = convert_to_sec(num, units)
        timestep_count = int(24. * 60. * 60. / frequency)
        frequency_flag = 'found frequency'
        return [frequency, frequency_flag, timestep_count]

    @staticmethod
    def process_netcdf(netcdf=None):
        """Process a netCDF file into a dataframe and summary."""
        from . import static_attrs

        ds = xarray.Dataset()
        ds = xarray.open_dataset(
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
        """Parse a netcdf file to extract metadata information."""
        ds, df_summ = self.process_netcdf(netcdf=self.file_location)
        self.source = ds.attrs['source']
        self.logger = ds.attrs['logger']
        self.program_name = ds.attrs['program']
        self.datafile = ds.attrs['datafile']
        program_content = self.get_program()
        [
            self.frequency,
            self.frequency_flag,
            self.timestep_count
        ] = self.get_programmed_frequency(
            program_content=program_content,
            datafile=self.datafile,
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
        """Generate a fake File object for testing and development."""
        from random import choice
        from faker import Faker
        fake = Faker()
        this_file = File(
            datafile=choice(DATA_FILES),
            source=fake.word(),
            logger=fake.word(),
            filename=fake.word(),
            frequency=choice([.1, 60, 600, 1800]),
            variables=[Variable.generate_fake() for i in range(1, 10)]
        )
        return this_file
