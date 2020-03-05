from flask_restx import fields, Namespace

# Define the Namespace for user related routes
api = Namespace('users', description='Users related operations')


class Marshaller:
    self = api.model('self', {
        'href': fields.String
    })

    links = api.model('links', {
        'self': fields.Nested(self, skip_none=True)
    })

    user = api.model('user', {
        'id': fields.Integer,
        'username': fields.String,
        '_links': fields.Nested(links, skip_none=True)
    })

    users = api.model('users', {
        'users': fields.List(fields.Nested(user, skip_none=True)),
        '_links': fields.Nested(links, skip_none=True)
    })

