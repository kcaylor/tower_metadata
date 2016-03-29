"""User model for Mpala Tower application."""
from flask.ext.login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from datetime import datetime


def make_api_key():
    """Create a user API key."""
    import uuid
    return str(uuid.uuid4()).replace('-', '')


class User(UserMixin, db.Document):
    """User object definition for MongoEngine."""

    ROLES = ['admin', 'user', 'guest']

    confirmed = db.BooleanField(default=False)
    created = db.DateTimeField(default=datetime.now())
    updated = db.DateTimeField(default=datetime.now())
    username = db.StringField(max_length=64, unique=True)
    email = db.StringField(max_length=64, unique=True)
    password_hash = db.StringField(max_length=120)
    last_seen = db.DateTimeField()
    member_since = db.DateTimeField(default=datetime.utcnow())
    notebooks = db.IntField(
        default=0
    )
    pods = db.IntField(
        default=0
    )
    observations = db.IntField(
        default=0
    )
    api_key = db.StringField(
        max_length=64,
        unique=True,
        default=make_api_key()
    )
    role = db.StringField(
        choices=ROLES,
        default='user')

    phone_number = db.StringField()
    # updated = db.DateTimeField()
    # created = db.DateTimeField()
    meta = {
        'indexes': ['email', 'username', 'api_key'],
        'collection': 'users',
    }

    def can_edit(self):
        """Only admins can edit."""
        if self.role == 'admin':
            return True
        if self.role == 'guest':
            return False
        if self.role == 'user':
            return False
        return False

    def generate_reset_token(self, expiration=3600):
        """Generate a password reset token."""
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.get_id()})

    def reset_password(self, token, new_password):
        """Reset a user password."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.get_id():
            return False
        self.password = new_password
        self.save()
        return True

    def generate_confirmation_token(self, expiration=3600):
        """Generate a confirmation token."""
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.get_id()})

    def confirm(self, token):
        """Confirm a user."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.get_id():
            return False
        self.confirmed = True
        self.save()
        return True

    def ping(self):
        """Determine when user was last seen."""
        self.last_seen = datetime.utcnow()
        self.save()

    @property
    def password(self):
        """Password cannot be retrieved."""
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        if password:
            self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Verify a user-submitted password."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """User representation."""
        return '<User %r>' % self.username

    def __unicode__(self):
        """Return the user id."""
        return self.id

    def get_id(self):
        """Get the user id."""
        return unicode(self.id)

    def is_authenticated(self):
        """Determine if the user authenticated."""
        return True

    def is_active(self):
        """User is active."""
        return True

    def is_administrator(self):
        """User is administrator."""
        if self.role == 'admin':
            return True
        else:
            return False

    def is_anonymous(self):
        """User is anonymous."""
        return False

    @staticmethod
    def verify_api_key(api_key):
        """Verify the user API key."""
        return User.objects(api_key=api_key).first()

    @staticmethod
    def create_administrator():
        """Create an app administrator."""
        if User.objects(role='admin').count() > 0:
            return "Administrator already exists"
        import os
        admin = User(
            confirmed=True,
            username=os.environ.get('ADMIN_USER'),
            email=os.environ.get('ADMIN_EMAIL'),
            role='admin',
            api_key=os.environ.get('ADMIN_API_KEY')
        )
        admin.password = os.environ.get('ADMIN_PASSWORD')
        admin.save()

    @staticmethod
    def create_guest():
        """Create a guest user."""
        if User.objects(role='guest').count() > 0:
            return "Guest user already exists"
        guest = User(
            confirmed=True,
            username='guest',
            email='guest@pulsepod.io',
            role='guest',
            api_key=make_api_key()
        )
        guest.password = 'pulsepodguest'
        guest.save()

    @staticmethod
    def generate_fake(count=10):
        """Generate a fake user."""
        from faker import Faker
        fake = Faker()
        # fake.seed(3123)
        fake_users = []
        i = 0
        while i < count:
            user = User(
                confirmed=True,
                username=fake.user_name(),
                email=fake.safe_email(),
                api_key=make_api_key()
            )
            try:
                user.password = fake.md5()
                user.save()
                fake_users.append(user)
                i += 1
            except:
                pass
        return fake_users


class AnonymousUser(AnonymousUserMixin):
    """Anonymous User class for Mpala Tower App."""

    def can(self, permissions):
        """User Anonymous is always false."""
        return False

    def is_administrator(self):
        """User Anonymous is always false."""
        return False

    def get_id(self):
        """User Anonymous is always false."""
        return None

    def can_edit(self):
        """User Anonymous is always false."""
        return False

    def is_authenticated(self):
        """User Anonymous is always false."""
        return False

    def ping(self):
        """User Anonymous is always false."""
        return

    username = 'Guest'


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    """Load a user."""
    user = User.objects.with_id(user_id)
    return user
