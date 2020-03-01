from werkzeug import datastructures
from flask_restplus import reqparse


class Parsers:
    image_upload = reqparse.RequestParser()
    image_upload.add_argument('image',
                              type=datastructures.FileStorage,
                              required=True,
                              location='files',
                              help='Image file')
    image_upload.add_argument('title',
                              required=True)

    login = reqparse.RequestParser()
    login.add_argument('username', required=True)
    login.add_argument('password', required=True)

    create_client = reqparse.RequestParser()
    create_client.add_argument('client_name', required=True)
    create_client.add_argument('client_uri', required=True)
    create_client.add_argument('grant_type', required=True)
    create_client.add_argument('redirect_uri', required=True)
    create_client.add_argument('response_type', required=True)
    create_client.add_argument('scope', required=True)
    create_client.add_argument('token_endpoint_auth_method', required=True)

    register = reqparse.RequestParser()
    register.add_argument('username', required=True)
    register.add_argument('password', required=True)

    authorize = reqparse.RequestParser()
    authorize.add_argument('user_id', required=True)
