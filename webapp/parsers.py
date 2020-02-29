from werkzeug import datastructures
from flask_restplus import reqparse


class Parsers:
    image_upload = reqparse.RequestParser()
    image_upload.add_argument('image',
                              type=datastructures.FileStorage,
                              required=True,
                              help='Image file')

    register = reqparse.RequestParser()
    register.add_argument('username', help='This field cannot be blank', required=True)
    register.add_argument('password', help='This field cannot be blank', required=True)