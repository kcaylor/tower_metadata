from flask import render_template
from . import main
from run import Metadata


@main.route('/')
def index():
    metadata = Metadata.find_one()
    return render_template(
        'index.html',
        metadata=metadata)


@main.route('/this_week')
def this_week():
    return render_template('this_week.html')


@main.route('/last_week')
def last_week():
    return render_template('last_week.html')
