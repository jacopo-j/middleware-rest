#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask
from flask_restplus import Api
from flask_sqlalchemy import SQLAlchemy, event
from sqlalchemy.engine import Engine
from json import load

with open("webapp/schemas.json", "r") as fp:
    schemas = load(fp)

with open("webapp/config.json", "r") as fp:
    config = load(fp)

db = SQLAlchemy()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
api = Api(app)

# Import resources in the app context
with app.app_context():
    # Import resources
    from . import resources


db.init_app(app)


@app.before_first_request
def create_table():
    db.drop_all()
    db.create_all()


# Enable foreign key constraints checking
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()




