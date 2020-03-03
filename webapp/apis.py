from flask_restplus import Api
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
    }

}


api = Api(authorizations=authorizations,
          doc="/swagger",
          title='REST Middleware Imgur-like Demo',
          description='A REST backend to allow users to upload images and visualize them, powered by OAuth authentication')
api.add_namespace(users, '/api')
api.add_namespace(auth, '/auth')

