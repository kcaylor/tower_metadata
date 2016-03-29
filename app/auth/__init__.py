"""Authentication Views for Mpala Tower App."""
from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views
