from flask_restful import Resource, reqparse, Api
from flask import make_response
from .models import User, Image


class Index(Resource):
    def get(self):
        response = make_response('<h1>Hello World!</h1>')
        response.headers['content-type'] = 'text/html'
        return response


class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', help='This field cannot be blank', required=True)
        parser.add_argument('password', help='This field cannot be blank', required=True)
        data = parser.parse_args()
        if User.exists_by_id(data['id']):
            return {'message': 'User with id equal to {} already exists'.format(data['id'])}
        new_user = User(id=data['id'],
                        password=User.generate_hash(data['password']))
        try:
            new_user.save_to_db()
            # TODO JWT
            return {
                'message': 'User {} was created'.format(data['username'])
            }
        except:
            return {'message': 'Internal error'}


