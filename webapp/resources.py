from flask_restplus import Resource, reqparse, Api
from flask import make_response, jsonify
from sqlalchemy import func
from .models import User, Image
from webapp import db, schemas, api
from .util import UserBuilder, add_self


@api.route('/index')
class Index(Resource):
    def get(self):
        response = make_response('<h1>Hello World!</h1>')
        response.headers['content-type'] = 'text/html'
        return response


@api.route(schemas["register"])
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
            new_id = db.session.query(func.max(User.id)).scalar() + 1
        new_user = User(username=data['username'], id=new_id,
                        password=User.generate_hash(data['password']))
        try:
            db.session.add(new_user)
            db.session.commit()
            response = jsonify(success=True)
            return response
        except Exception as e:
            print(e)
            return {'message': 'Internal error'}


@api.route(schemas["users"])
class UsersQuery(Resource):
    # TODO add AUTH required
    def get(self):
        users = [UserBuilder(id, username) for id,username in db.session.query(User.id, User.username)]
        response = dict()
        response["users"] = users
        add_self(response, schemas["users"])
        return response








