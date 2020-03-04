import uuid

import boto3
from botocore.exceptions import ClientError
from flask import make_response, jsonify
from flask_restx import Resource, Namespace, fields
from werkzeug.utils import redirect

from webapp.api.model import User, Image
from webapp.modules import schemas, db, config
from webapp.auth.oauth2 import require_oauth
from webapp.parsers import Parsers
from webapp.util import UserBuilder, add_self, ImageBuilder, get_mimetype, check_size_type, current_user

# Define the Namespace for user related routes
api = Namespace('users', description='Users related operations')

# Define grants that allows to access the different resources
security_grants = [{'oauth2_implicit': ['profile']}, {'oauth2_password': ['profile']}, {'oauth2_code': ['profile']}]


@api.route(schemas["register"])
class Register(Resource):
    @api.response(200, description='Registration was successful')
    @api.response(400, description='Registration was unsuccessful')
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
            return jsonify(success=False), 400


@api.route(schemas["users"])
class UsersQuery(Resource):
    @api.response(200, description='List of users registered with their info')
    @api.response(401, description='Unauthorized')
    @api.doc(security=security_grants)
    @require_oauth('profile')
    def get(self):
        users = [UserBuilder(id, username) for id,username in db.session.query(User.id, User.username)]
        response = dict()
        response["users"] = users
        add_self(response, schemas["users"])
        return response


@api.route(schemas["user"].format(id="<user_id>"))
class ImagesQuery(Resource):
    @api.response(200, description="List of images of the selected user")
    @api.response(401, description="Unauthorized")
    @api.response(400, description="User with given name wasn't found")
    @api.doc(security=security_grants)
    @require_oauth('profile')
    def get(self, user_id):
        if not User.exists_by_id(user_id):
            return jsonify(message="User with given name doesn't exist"), 400
        selected_images = Image.query.filter_by(user_id=user_id).all()
        images = [ImageBuilder(user_id, image.id, image.guid, image.title) for image in selected_images]
        response = dict()
        response["id"] = user_id
        response["images"] = images
        add_self(response, schemas["user"].format(id=user_id))
        return response


@api.route(schemas['upload'])
class ImageUpload(Resource):
    @api.response(401, description="Unauthorized")
    @api.response(400, description="Upload wasn't successful")
    @api.response(200, description="Upload was successful")
    @api.doc(security=security_grants)
    @api.expect(Parsers.image_upload, validate=True)
    def post(self):
        user_id = current_user().id
        bucket = boto3.resource('s3').Bucket(config['bucket_name'])
        data = Parsers.image_upload.parse_args()
        new_guid = uuid.uuid4().hex
        new_image = Image(title=data['title'], user_id=user_id, guid=new_guid)
        new_file = data['image'].read()
        new_type = get_mimetype(new_file)
        if not check_size_type(new_type, new_file):
            return jsonify(success=False), 400
        bucket.put_object(Body=new_file, Key=new_guid, ContentType=new_type, ACL='public-read')
        db.session.add(new_image)
        db.session.commit()
        return jsonify(success=True)


@api.route(schemas["image"].format(user_id="<user_id>", image_id="<image_id>"))
class Image(Resource):
    @api.response(200, description="Information about the selected image")
    @api.response(400, description="Selected image doesn't exist")
    @api.response(401, description="Unauthorized")
    @api.doc(security=security_grants)
    @require_oauth('profile')
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

    @api.response(200, description="Delete was successful")
    @api.response(400, description="An error occurred during the delete")
    @api.response(401, description="Unauthorized")
    @api.doc(security=security_grants)
    @require_oauth('profile')
    def delete(self, user_id, image_id):
        if user_id != current_user().id:
            return jsonify(success=False), 401
        image = Image.query.filter_by(id=image_id, user_id=user_id).first()
        if not image:
            return jsonify(succes=False), 400
        # Delete S3 Object
        s3 = boto3.resource('s3')
        try:
            s3.Object(config['bucket_name'], image.guid).delete()
        except ClientError as e:
            return jsonify(aws_error=e.response['Error']['Code']), 400
        # Delete SQL Object
        Image.query.filter_by(id=image_id).delete()
        db.session.commit()
        return jsonify(success=True)


@api.route(schemas["image"].format(user_id="<user_id>", image_id="<image_id>")+"/get")
class ImageStorage(Resource):
    @api.response(200, description="Redirect to the image file")
    @api.doc(security=security_grants)
    @require_oauth('profile')
    def get(self, user_id, image_id):
        image_guid = Image.query.filter_by(id=image_id, user_id=user_id).first().guid
        redirect(config["storage"].format(bucket_name=config["bucket_name"], guid=image_guid))
