from flask import Flask
from flask_sqlalchemy import SQLAlchemy
# from flask_migrate import Migrate,MigrateCommand
# from flask_script import Manager
import uuid
import sys,os



app = Flask(__name__)
app.config.from_object('app.config')
app.config['SECRET_KEY'] = 'the quick brown fox jumps over the lazy dog'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../db.sqlite'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = str(uuid.uuid4())


db = SQLAlchemy(app) 
# manager = Manager(app)
# manager.add_command('db', MigrateCommand)


 
from .views import register_blueprints
register_blueprints(app)


 
