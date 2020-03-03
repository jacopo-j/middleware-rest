from flask_restx import Api
from .auth.routes import api as auth
from .api.routes import api as users
from webapp import schemas

authorizations = {
    'oauth2_code': {
        'type': 'oauth2',
        'flow': 'authorizationCode',
        'tokenUrl': '/auth' + schemas['issue_token'],
        'authorizationUrl': 'auth' + schemas['authorize'],
        'scopes': {
            'profile': 'auth',
        }
    },
    'oauth2_password': {
        'type': 'oauth2',
        'flow': 'password',
        'tokenUrl': '/auth' + schemas['issue_token'],
        'authorizationUrl': 'auth' + schemas['authorize'],
        'scopes': {
            'profile': 'auth',
        }
    },
    'oauth2_implicit': {
        'type': 'oauth2',
        'flow': 'implicit',
        'tokenUrl': '/auth' + schemas['issue_token'],
        'authorizationUrl': 'auth' + schemas['authorize'],
        'scopes': {
            'profile': 'auth',
        }
    }
}

with open("webapp/swagger_description.md", "r") as fp:
    description = fp.read()

api = Api(authorizations=authorizations,
          doc="/swagger",
          title='REST Middleware Imgur-like Demo',
          description=description)
api.add_namespace(users, '/api')
api.add_namespace(auth, '/auth')


