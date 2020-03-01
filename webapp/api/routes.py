import uuid

import boto3
from flask import make_response, jsonify
from flask_restplus import Resource
from werkzeug.utils import redirect

from webapp.api.model import User, Image
from webapp.modules import api, schemas, db, config
from webapp.auth.oauth2 import require_oauth
from webapp.parsers import Parsers
from webapp.util import UserBuilder, add_self, ImageBuilder, get_mimetype, check_size_type


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


@api.route(schemas["image"].format(user_id="<user_id>", image_id="<image_id>")+"/get")
class ImageStorage(Resource):
    def get(self, user_id, image_id):
        image_guid = Image.query.filter_by(id=image_id, user_id=user_id).first().guid
        redirect(config["storage"].format(bucket_name=config["bucket_name"], guid=image_guid))