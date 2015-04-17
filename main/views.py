from flask import render_template
from . import main


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/this_week')
def this_week():
    return render_template('this_week.html')


@main.route('/last_week')
def last_week():
    return render_template('last_week.html')
