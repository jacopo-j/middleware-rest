from authlib.integrations.flask_oauth2 import current_token
from flask_restplus import Resource, reqparse, Api
from flask import make_response, jsonify, request, session, redirect, render_template
from oauthlib.oauth2 import OAuth2Error
from sqlalchemy import func
from .models import db, User, Image, OAuth2Client
from webapp import schemas, config, api
from .util import UserBuilder, ImageBuilder, add_self, check_size_type, get_mimetype
from .parsers import Parsers
from .oauth2 import authorization, require_oauth
from werkzeug.security import gen_salt
import time
import uuid
import boto3


def current_user():
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None


def split_by_crlf(s):
    return [v for v in s.splitlines() if v]


@api.route('/index')
class Index(Resource):
    def get(self):
        response = make_response('<h1>Hello World!</h1>')
        response.headers['content-type'] = 'text/html'
        return response


@api.route(schemas["register"])
class Register(Resource):
    @api.expect(Parsers.register, validate=True)
    def post(self):
        data = Parsers.register.parse_args()
        if User.exists_by_username(data['username']):
            return {'message': 'User with username equal to {} already exists'.format(data['username'])}
        new_user = User(username=data['username'],
                        password=User.generate_hash(data['password']))
        try:
            db.session.add(new_user)
            db.session.commit()
            return jsonify(success=True)
        except Exception as e:
            print(e)
            return {'message': 'Internal error'}


@api.route(schemas["users"])
class UsersQuery(Resource):
    @require_oauth('profile')
    def get(self):
        users = [UserBuilder(id, username) for id,username in db.session.query(User.id, User.username)]
        response = dict()
        response["users"] = users
        add_self(response, schemas["users"])
        return response


@api.route(schemas["user"].format(id="<user_id>"))
class ImagesQuery(Resource):
    # TODO add AUTH required
    def get(self, user_id):
        if not User.exists_by_id(user_id):
            return jsonify(message="User with given name doesn't exist")
        selected_images = Image.query.filter_by(user_id=user_id).all()
        images = [ImageBuilder(user_id, image.id, image.guid, image.title) for image in selected_images]
        response = dict()
        response["id"] = user_id
        response["images"] = images
        add_self(response, schemas["user"].format(id=user_id))
        return response


@api.route(schemas['upload'])
class ImageUpload(Resource):
    @api.expect(Parsers.image_upload)
    def post(self):
        # TODO change to the related authenticated user
        user_id = 1
        bucket = boto3.resource('s3').Bucket(config['bucket_name'])
        data = Parsers.image_upload.parse_args()
        new_guid = uuid.uuid4().hex
        new_image = Image(title=data['title'], user_id=user_id, guid=new_guid)
        new_file = data['image'].read()
        new_type = get_mimetype(new_file)
        if not check_size_type(new_type, new_file):
            return jsonify(success=False)
        bucket.put_object(Body=new_file, Key=new_guid, ContentType=new_type, ACL='public-read')
        db.session.add(new_image)
        db.session.commit()
        return jsonify(success=True)


@api.route('/login')
class Login(Resource):
    def post(self):
        data = Parsers.login.parse_args()
        user = User.query.filter_by(username=data["username"]).first()
        if not user or not user.check_password(data["password"]):
            # TODO login failed
            return {'message': 'Login failed'}
        session['id'] = user.id
        # TODO login succeeded
        return {'message': 'Login succeeded'}


@api.route('/create_client')
class CreateClient(Resource):
    def post(self):
        user = current_user()
        if not user:
            return {'message': 'Login required'}

        client_id = gen_salt(24)
        client_id_issued_at = int(time.time())
        client = OAuth2Client(
            client_id=client_id,
            client_id_issued_at=client_id_issued_at,
            user_id=user.id,
        )

        if client.token_endpoint_auth_method == 'none':
            client.client_secret = ''
        else:
            client.client_secret = gen_salt(48)

        data = Parsers.create_client.parse_args()
        client_metadata = {
            "client_name": data["client_name"],
            "client_uri": data["client_uri"],
            "grant_types": split_by_crlf(data["grant_type"]),
            "redirect_uris": split_by_crlf(data["redirect_uri"]),
            "response_types": split_by_crlf(data["response_type"]),
            "scope": data["scope"],
            "token_endpoint_auth_method": data["token_endpoint_auth_method"]
        }
        client.set_client_metadata(client_metadata)
        db.session.add(client)
        db.session.commit()
        return {'message': 'Client created successfully', 'client_id': client.client_id, 'client_secret': client.client_secret}


@api.route('/oauth/authorize')
class Authorize(Resource):
    def post(self):
        data = Parsers.authorize.parse_args()
        user = User.query.filter_by(id=data['user_id']).first()
        return authorization.create_authorization_response(grant_user=user)


@api.route('/oauth/token')
class IssueToken(Resource):
    def post(self):
        return authorization.create_token_response()


@api.route('/oauth/revoke')
class RevokeToken(Resource):
    def post(self):
        return authorization.create_endpoint_response('revocation')


@api.route(schemas["image"].format(user_id="<user_id>", image_id="<image_id>"))
class Image(Resource):
    def get(self, user_id, image_id):
        image = Image.query.filter_by(id=image_id, user_id=user_id).first()
        response = dict()
        response["id"] = image_id
        response["title"] = image.title
        response["user_id"] = user_id
        response["url"] = config["storage"].format(bucket_name=config["bucket_name"], guid=image.guid)
        add_self(self, schemas["image"].format(user_id=user_id, image_id=image.guid))
        user_link = dict()
        user_link["href"] = schemas["user"].format(id=user_id)
        response["_links"]["user"] = user_link
        return response


@api.route(schemas["image"].format(user_id="<user_id>", image_id="<image_id>")+"/get")
class ImageStorage(Resource):
    def get(self, user_id, image_id):
        image_guid = Image.query.filter_by(id=image_id, user_id=user_id).first().guid
        redirect(config["storage"].format(bucket_name=config["bucket_name"], guid=image_guid))