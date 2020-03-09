from os import environ

import boto3
from flask import Flask, redirect
from flask_sqlalchemy import SQLAlchemy
from json import load
from pathlib import Path


path = Path(__file__).parent


db = SQLAlchemy()

with open(path / "../schemas.json", "r") as fp:
    schemas = load(fp)

with open(path / "../config.json", "r") as fp:
    config = load(fp)

app = Flask(__name__, template_folder="templates")
app.config["SECRET_KEY"] = "3205fc85cd004116bfe218f14192e49a"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SWAGGER_UI_OAUTH_CLIENT_ID"] = "documentation"
domain = app.config.get("SERVER_NAME")


port = environ.get("PORT", config["default_port"])
redirect_uri = environ.get("REDIRECT_URI", config["redirect_uri"])
client_uri = environ.get("CLIENT_URI", config["client_uri"])

client_s3 = boto3.resource("s3")


@app.route("/")
def redirect_to_swagger():
    return redirect("/swagger", 302)



