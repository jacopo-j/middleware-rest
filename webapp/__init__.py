#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

from flask_sqlalchemy import event
from sqlalchemy.engine import Engine
from werkzeug.security import gen_salt

from webapp.api.model import User
from webapp.auth.model import OAuth2Client
from webapp.auth.oauth2 import config_oauth
from .modules import app, db, config, port
from passlib.hash import pbkdf2_sha256 as sha256


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


def init_auth_db():
    db.drop_all()
    db.create_all()
    new_user = User(username="documentation",
                    password=sha256.hash("documentation"))
    db.session.add(new_user)
    db.session.commit()
    client_id = "documentation"
    client_id_issued_at = int(time.time())

    client = OAuth2Client(
        client_id=client_id,
        client_id_issued_at=client_id_issued_at,
        user_id="1",
    )

    client.client_secret = 'secret'

    uri = "http://{}:{}/swaggerui/oauth2-redirect.html".format(config['host'], port)
    client_metadata = {
        "client_name": "documentation",
        "client_uri": uri,
        "grant_types": ["password", "authorization_code"],
        "redirect_uris": uri,
        "response_types": "code",
        "scope": "profile",
        "token_endpoint_auth_method": "client_secret_basic"
    }
    client.set_client_metadata(client_metadata)
    db.session.add(client)
    db.session.commit()


@app.before_first_request
def create_table():
    db.drop_all()
    db.create_all()
    init_auth_db()


# Enable foreign key constraints checking
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()



