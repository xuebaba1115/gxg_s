# coding:utf8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import uuid
import sys
import os

abs=os.path.abspath('.')

app = Flask(__name__)
app.config.from_object('app.config')
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////%s/db.sqlite'%(abs)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite' (windows)
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = str(uuid.uuid4())


db = SQLAlchemy(app)


from .views import register_blueprints
register_blueprints(app)
