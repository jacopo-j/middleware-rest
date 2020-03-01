#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask_sqlalchemy import event
from sqlalchemy.engine import Engine
from webapp.auth.oauth2 import config_oauth
from .modules import app, db


def create_app():
    # Import resources in the app context
    with app.app_context():
        # Import resources
        from .api import routes
        from .auth import routes
    # Configure db and auth
    db.init_app(app)
    config_oauth(app)
    return app


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




