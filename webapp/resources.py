from flask_restful import Resource
from flask import make_response


class Index(Resource):

    def get(self):
        response = make_response('<h1>Hello World!</h1>')
        response.headers['content-type'] = 'text/html'
        return response
