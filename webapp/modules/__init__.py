from flask import Flask
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from json import load


db = SQLAlchemy()

with open("webapp/schemas.json", "r") as fp:
    schemas = load(fp)

with open("webapp/config.json", "r") as fp:
    config = load(fp)

app = Flask(__name__)
app.config['SECRET_KEY'] = '3205fc85cd004116bfe218f14192e49a'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
domain = app.config.get('SERVER_NAME')

authorizations = {
    'oauth2_password': {
        'type': 'oauth2',
        'flow': 'password',
        'tokenUrl': schemas['issue_token'],
        'authorizationUrl': schemas['authorize'],
        'scopes': {
            'profile': 'auth',
        }
    },
    'oauth2_code': {
        'type': 'oauth2',
        'flow': 'authorizationCode',
        'tokenUrl': schemas['issue_token'],
        'authorizationUrl': schemas['authorize'],
        'scopes': {
            'profile': 'auth',
        }
    }
}

app.config['SWAGGER_UI_OAUTH_CLIENT_ID'] = 'documentation'
app.config['SWAGGER_UI_OAUTH_REDIRECT_URL'] = '/authorize'
api = Api(app, authorizations=authorizations, doc="/swagger", template_folder='templates')

