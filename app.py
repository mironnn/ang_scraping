import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask import json

from cors_decorator import crossdomain

app = Flask(__name__, template_folder='templates')

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
app.config['SQLALCHEMY_MIGRATE_REPO'] = os.path.join(basedir, 'db_repository')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

from models import Vacancy, Location
db.create_all()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/my', methods=['GET', 'OPTIONS'])
@crossdomain(origin='*')
def angul():
    data_list = {i.id: i.serialize for i in Vacancy.query.all()[0:10]}
    return json.dumps({'data': data_list})
