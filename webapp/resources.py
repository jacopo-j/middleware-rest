from flask_restful import Resource, reqparse, Api
from flask import make_response
from sqlalchemy import func

from .models import User, Image
from webapp import db


class Index(Resource):
    def get(self):
        response = make_response('<h1>Hello World!</h1>')
        response.headers['content-type'] = 'text/html'
        return response


class Register(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('username', help='This field cannot be blank', required=True)
        parser.add_argument('password', help='This field cannot be blank', required=True)
        data = parser.parse_args()
        if User.exists_by_username(data['username']):
            return {'message': 'User with username equal to {} already exists'.format(data['username'])}
        new_id = 0
        if db.session.query(User).first():
            new_id = db.session.query(func.max(User.id))
        new_user = User(username=data['username'], id=new_id,
                        password=User.generate_hash(data['password']))
        try:
            db.session.add(new_user)
            db.session.commit()
            # TODO JWT
            return {
                'message': 'User {} was created'.format(data['username'])
            }
        except Exception as e:
            print(e)
            return {'message': 'Internal error'}


