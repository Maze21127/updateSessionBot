from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPTokenAuth

from settings import SECRET_KEY

db = SQLAlchemy()

app = Flask(__name__)
app.config.from_pyfile('../settings.py')

app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.config['JSON_AS_ASCII'] = False
app.config['SECRET_KEY'] = SECRET_KEY
app.config['UPLOAD_FOLDER'] = 'static/files'
db.init_app(app)

auth = HTTPTokenAuth(scheme='Bearer')

manager = LoginManager(app)

from . import views

