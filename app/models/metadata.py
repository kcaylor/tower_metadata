from . import db
import errno
from .file import File


def write_temp(client, file_location, this_file, f):
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
    out = open(temp_location, 'wb')
    with client.get_file(file_location) as f:
        out.write(f.read())
    out.close()
    print(temp_location)
    return temp_location


# The Metadata object
class Metadata(db.DynamicDocument):

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
        return '<Metadata for doy: %d, year: %d>' % (self.doy, self.year)

    def get_id(self):
        return unicode(self.id)

    # Look for files in a file system. We will subclass this class
    # to create a system that looks for files on Dropbox, etc...
    @staticmethod
    def find_files(year=None, doy=None):
        import os
        from posixpath import join
        root_dir = os.environ.get('ROOT_DIR')
        files = []  # Initialize an empty array
        f = 'raw_MpalaTower_%i_%03d.nc' % (year, doy)
        for this_file in File.DATA_FILES:
            if f in os.listdir(join(root_dir, this_file)):
                file_location = join(root_dir, this_file, f)
                this_file = File(
                    filename=f,
                    datafile=this_file,
                    file_location=file_location,
                )
                files.append(this_file)
        return files

    def generate_metadata(self):
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
        return self

    def parse_files(self):
        for f in self.files:
            f.parse()
        self.save()

    @staticmethod
    def generate_fake(count=10):
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

    def __repr__(self):
        return '<Dropbox Metadata for doy: %d, year: %d>' \
            % (self.doy, self.year)

    @staticmethod
    def find_files(year=None, doy=None):
        from dropbox.client import DropboxClient
        from posixpath import join
        import os

        access_token = os.environ.get('access_token')
        dropbox_dir = os.environ.get('dropbox_dir')

        client = DropboxClient(access_token)

        files = []  # Initialize an empty array
        f = 'raw_MpalaTower_%i_%03d.nc' % (year, doy)
        for this_file in File.DATA_FILES:
            file_location = join(dropbox_dir, this_file)
            listdict = []
            # listdict has a good metadata in it if we ever decide to use it
            listdict = client.search(file_location, f, file_limit=1)
            if listdict != []:
                temp_location = write_temp(
                    client,
                    listdict[0]['path'],
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
