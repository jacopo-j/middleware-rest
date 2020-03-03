import os

from flask import Flask, redirect
from flask_restplus import Api
from flask_sqlalchemy import SQLAlchemy
from json import load


db = SQLAlchemy()

with open("webapp/schemas.json", "r") as fp:
    schemas = load(fp)

with open("webapp/config.json", "r") as fp:
    config = load(fp)

app = Flask(__name__, template_folder="templates")
app.config['SECRET_KEY'] = '3205fc85cd004116bfe218f14192e49a'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SWAGGER_UI_OAUTH_CLIENT_ID'] = 'documentation'
domain = app.config.get('SERVER_NAME')


try:
    port = os.environ["PORT"]
except KeyError as e:
    port = config["default_port"]


@app.route('/')
def redirect_to_swagger():
    return redirect('/swagger', 302)



