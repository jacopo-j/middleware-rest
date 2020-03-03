#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time

from flask import request, redirect
from flask_restx import Api
from flask_sqlalchemy import event
from sqlalchemy import func
from sqlalchemy.engine import Engine
from werkzeug.security import gen_salt

from webapp.api.model import User
from webapp.auth.model import OAuth2Client
from webapp.auth.oauth2 import config_oauth
from .modules import app, db, config, port, schemas
from passlib.hash import pbkdf2_sha256 as sha256
from .apis import api


def create_app():
    """ Configure db and auth """
    db.init_app(app)
    config_oauth(app)
    api.init_app(app)
    return app


def init_auth_db():
    db.drop_all()
    db.create_all()
    client_id = "documentation"
    init_developer_client(dev_username=client_id,
                          dev_password=client_id,
                          client_id=client_id,
                          grants=["password", "authorization_code"],
                          response_types="code",
                          auth_method="client_secret_basic")
    client_id = "dummy"
    init_developer_client(dev_username=client_id,
                          dev_password=client_id,
                          client_id=client_id,
                          grants=["implicit"],
                          response_types="token",
                          auth_method="none")


@app.before_first_request
def create_table():
    db.drop_all()
    db.create_all()
    init_auth_db()


# Redirect HTTP to HTTPS when running in production
@app.before_request
def before_request():
    if (
            not request.url.startswith('http://127.0.0.1') and
            not request.url.startswith('http://0.0.0.0') and
            not request.is_secure):
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)


# Enable foreign key constraints checking
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()


def init_developer_client(dev_username, dev_password, client_id, grants, response_types, auth_method):
    """ Initialize a developer user with the related client"""
    new_user = User(username=dev_username,
                    password=sha256.hash(dev_password))
    db.session.add(new_user)
    db.session.commit()
    new_id = db.session.query(func.max(User.id)).scalar()
    client_id_issued_at = int(time.time())

    client = OAuth2Client(
        client_id=client_id,
        client_id_issued_at=client_id_issued_at,
        user_id=new_id,
    )

    # TODO Change in production
    client.client_secret = 'secret'

    uri = "http://{}:{}/swaggerui/oauth2-redirect.html".format(config['host'], port)
    client_metadata = {
        "client_name": dev_username,
        "client_uri": uri,
        "grant_types": grants,
        "redirect_uris": uri,
        "response_types": response_types,
        "scope": "profile",
        "token_endpoint_auth_method": auth_method
    }
    client.set_client_metadata(client_metadata)
    db.session.add(client)
    db.session.commit()
