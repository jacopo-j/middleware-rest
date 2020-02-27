#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from . import resources

db = SQLAlchemy()

app = Flask(__name__)
db.init_app(app)

api = Api(app)
api.add_resource(resources.Index, '/')
