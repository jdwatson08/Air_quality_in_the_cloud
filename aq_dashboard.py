# pylint: disable=no-member
"""OpenAQ Air Quality Dashboard with Flask."""
import openaq
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(app)
api = openaq.OpenAQ()


class Record(DB.Model):
    '''Defines the record class'''
    # id (integer, primary key)
    id = DB.Column(DB.Integer, primary_key=True)
    # datetime (string)
    datetime = DB.Column(DB.String(25))
    # value (float, cannot be null)
    value = DB.Column(DB.Float, nullable=False)

    def __init__(self, datetime, value):
        self.datetime = datetime
        self.value = value

    def __repr__(self):
        return f'Time: {self.datetime}, Value: {self.value}'


@app.route('/')
def root():
    """Base view."""
    results_string = Record.query.filter(Record.value >= 18).all()
    return f'{results_string}'


@app.route('/refresh')
def refresh():
    """Pull fresh data from Open AQ and replace existing data."""
    DB.drop_all()
    DB.create_all()
    for i in get_results(api):
        records = Record(datetime=str(i[0]), value=i[1])
        DB.session.add(records)
        DB.session.commit()
    return 'Data refreshed!'


def get_results(api=openaq.OpenAQ()):
    '''Returns a list of tuples from the pulled data. Each tuple
    contains the datetime and value for each observation'''
    _, get_tuple = api.measurements(city="Los Angeles", parameter='pm25')
    observations = []
    for i in get_tuple['results']:
        new = (i['date']['utc'], i['value'])
        observations.append((new))
    return observations
