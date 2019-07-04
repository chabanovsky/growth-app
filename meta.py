import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_babel import Babel

from local_settings import FLASK_SECRET_KEY, PG_NAME_PASSWORD, STACKEXCHANGE_CLIENT_SECRET, STACKEXCHANGE_CLIENT_KEY, STACKEXCHANGE_CLIENT_ID

def make_db_session(engine):
    return scoped_session(sessionmaker(autocommit=False,
        autoflush=True,
        bind=engine))

def make_db_engine():
    return create_engine(app.config['SQLALCHEMY_DATABASE_URI'], convert_unicode=True)

APP_URL = "http://growth.rudevs.ru"
DB_NAME = "growth_app"
STACKOVERFLOW_HOSTNAME = "stackoverflow.com"
STACKOVERFLOW_SITE_PARAM = "stackoverflow"

app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = FLASK_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://' + PG_NAME_PASSWORD + '@localhost:5432/'+ DB_NAME + '?client_encoding=utf8'
#app.config['BABEL_DEFAULT_LOCALE'] = LANGUAGE

engine = make_db_engine()
db_session = make_db_session(engine)

db = SQLAlchemy(app)

babel = Babel(app)

STACKEXCHANGE_CLIENT_SECRET = STACKEXCHANGE_CLIENT_SECRET
STACKEXCHANGE_CLIENT_KEY = STACKEXCHANGE_CLIENT_KEY
STACKEXCHANGE_CLIENT_ID = STACKEXCHANGE_CLIENT_ID