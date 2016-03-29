"""Main views for Tower Metadata app."""
from . import main
from app.models import Metadata
from flask import render_template


# Set up the application routes:
@main.route('/')
def index():
    """App index route."""
    metadata = Metadata.objects().first()
    return render_template(
        'index.html',
        metadata=metadata)


@main.route('/<int:year>/<int:doy>')
def file_year_doy(year=None, doy=None):
    """Return metadata for a specific year and day of year."""
    from datetime import datetime
    metadata = Metadata.objects(
        year=year,
        doy=doy).first()
    jan1 = datetime(year=year, month=1, day=1)
    date = datetime.fromordinal(jan1.toordinal() + doy - 1)
    if metadata is None:
        return render_template(
            'build_metadata.html',
            date=date,
            doy=doy
        )
    else:
        return render_template(
            'file.html',
            metadata=metadata)


@main.route('/<int:year>/<int:month>/<int:day>')
def file_year_month_day(year=2015, month=1, day=20):
    """Return metadata for a specific year, month, and day."""
    from datetime import datetime
    date = datetime(year=year, month=month, day=day)
    metadata = Metadata.objects(
        date=date).first()
    if metadata is None:
        return render_template('404.html')
    else:
        return render_template(
            'file.html',
            metadata=metadata)
