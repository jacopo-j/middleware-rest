#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
api = Api(app)

with app.app_context():
    # Import resources
    from . import resources
    api.add_resource(resources.Index, '/')
    api.add_resource(resources.Register, '/register')


db.init_app(app)


@app.before_first_request
def create_table():
    db.drop_all()
    db.create_all()




