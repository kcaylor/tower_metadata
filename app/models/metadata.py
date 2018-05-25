"""Definition of the Metadata class for Mpala Tower Data."""
from . import db, DATA_FILES
import errno
from .file import File
from slacker import Slacker
from datetime import datetime
import os

slack = Slacker(os.environ.get('SLACK_TOKEN'))

netcdf_location = 'raw_netCDF_output'

def write_temp(client, file_location, this_file, f):
    """Write temporary files on heroku."""
    import os
    # this is probably not a good place to store them
    # the actual code
    path = '/tmp/%s/' % this_file
    try:
        os.mkdir(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
    temp_location = '/tmp/%s/' % this_file + f
    # Check to see if the file is already there. It's faster.
    if not os.path.isfile(temp_location):
        client.files_download_to_file(temp_location, file_location)
        # out = open(temp_location, 'wb')

        # with client.files_download(file_location) as f:
        #     out.write(f.read())
        # out.close()
    print(temp_location)
    return temp_location


# The Metadata object
class Metadata(db.DynamicDocument):
    """Define the Metadata Object model in Mongoengine."""

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
    created = db.DateTimeField(default=datetime.now())
    summary = db.StringField()
    conventions = db.StringField()
    naming_authority = db.StringField()  # or URLField?
    # The Metadata object contains a list of Files:
    files = db.EmbeddedDocumentListField(File)

    meta = {
        'allow_inheritance': True,
        'collection': 'metadata',
        'ordering': ['-date'],
        'index_background': True,
        'indexes': [
            'year',
            'month',
            'doy',
        ]
    }

    def __repr__(self):
        """Representation of the Metadata class for the Mpala Tower."""
        return '<Metadata for doy: %d, year: %d>' % (self.doy, self.year)

    def get_id(self):
        """Metadata object ID on the MongoDb."""
        return unicode(self.id)

    # Look for files in a file system. We will subclass this class
    # to create a system that looks for files on Dropbox, etc...
    @staticmethod
    def find_files(year=None, doy=None):
        """Find NetCDF files for this year and doy."""
        import os
        from posixpath import join
        root_dir = os.environ.get('ROOT_DIR')
        files = []  # Initialize an empty array
        f = 'raw_MpalaTower_%i_%03d.nc' % (year, doy)
        for this_file in DATA_FILES:
            if f in os.listdir(join(root_dir, this_file)):
                file_location = join(root_dir, this_file, f)
                this_file = File(
                    filename=f,
                    datafile=this_file,
                    file_location=file_location,
                )
                files.append(this_file)
            else:
                continue
        return files

    def generate_metadata(self):
        """Generate metadata from list of metadata files."""
        if len(self.files) > 0:
            this_netcdf = self.files[0].file_location
            ds, df_summ = self.files[0].process_netcdf(netcdf=this_netcdf)
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
            if self.date is None:
                from datetime import datetime
                self.date = datetime.fromordinal(
                    datetime.toordinal(datetime(
                        year=self.year, month=1, day=1)
                    ) + self.doy - 1
                )
                self.month = self.date.month
                self.day = self.date.day
            self.parse_files()
            self.save()
            slack.chat.post_message(
                '#mpalatower',
                self.slack(),
                username='Mpala Tower',
                icon_emoji=':package:')
            return self
        else:
            return "No files found for %d, day of year %d" \
                % (self.year, self.doy)

    def parse_files(self):
        """Parse the NetCDF file list."""
        for f in self.files:
            f.parse()
        self.save()

    def slack(self):
        """Report metadata progress to Slack."""
        import os
        url = os.environ.get('APP_URL')
        link = "{url}/{year}/{doy}".format(
            url=url,
            year=self.year,
            doy=self.doy)
        return "Created metadata for {mon}/{day}/{year}\n{link}".format(
            mon=self.month,
            day=self.day,
            year=self.year,
            link=link)

    @staticmethod
    def generate_fake(count=10):
        """Generate fake metadata objects for testing and development."""
        from random import randint
        from faker import Faker
        fake = Faker()
        fake_metadata = []
        for i in range(count):
            this_metadata = Metadata(
                license=fake.word(),
                title=fake.sentence(),
                creator=fake.name(),
                creator_email=fake.email(),
                institution=fake.company(),
                aknowledgements=fake.sentence(),
                feature_type=fake.word(),
                year=int(fake.year()),
                month=int(fake.month()),
                doy=randint(1, 365),
                date=fake.date_time_this_month(),
                summary=fake.sentence(),
                conventions=fake.word(),
                naming_authority=fake.company(),
                files=[File.generate_fake() for i in range(1, 5)]
            )
            fake_metadata.append(this_metadata)
            this_metadata.save()
        if len(fake_metadata) == 1:
            return fake_metadata[0]
        else:
            return fake_metadata


class DropboxFiles(Metadata):
    """Dropbox Metadata Class for the Mpala Tower."""

    def __repr__(self):
        """Representation of Dropbox Metadata class."""
        return '<Dropbox Metadata for doy: %d, year: %d>' \
            % (self.doy, self.year)

    @staticmethod
    def find_files(year=None, doy=None):
        """Find netcdf files correponding to year and doy on Dropbox."""
        from dropbox import Dropbox
        from posixpath import join
        import os

        access_token = os.environ.get('access_token')
        dropbox_dir = os.environ.get('dropbox_dir')

        client = Dropbox(access_token)

        files = []  # Initialize an empty array
        f = 'raw_MpalaTower_{year}_{doy:03d}.nc'.format(
            year=year, doy=doy)
        program_list = DATA_FILES
        program_list.remove('unknown')
        for this_file in program_list:
            file_location = join(dropbox_dir, netcdf_location, this_file)
            matches = []
            # listdict has a good metadata in it if we ever decide to use it
            results = client.files_search(file_location, f, max_results=1)
            matches = results.matches
            if matches:
                match = matches[0]
                temp_location = write_temp(
                    client,
                    match.metadata.path_display,
                    this_file,
                    f
                )
                this_file = File(
                    filename=f,
                    datafile=this_file,
                    file_location=temp_location,
                )
                files.append(this_file)
            else:
                continue
        return files
