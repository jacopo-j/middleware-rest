import uuid

import boto3
from authlib.integrations.flask_oauth2 import current_token
from botocore.exceptions import ClientError
from flask_restx import Resource
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import redirect

from webapp.api.model import User, Image
from webapp.modules import schemas, db, config
from webapp.auth.oauth2 import require_oauth
from webapp.parsers import Parsers
from webapp.util import UserBuilder, add_self, ImageBuilder, get_mimetype, check_size_type
from .marshaller import api, Marshaller

# Define grants that allows to access the different resources
security_grants = [{"oauth2_implicit": ["profile"]}, {"oauth2_password": ["profile"]}, {"oauth2_code": ["profile"]}]


@api.route(schemas["register"])
class Register(Resource):
    @api.response(200, description="Registration was successful")
    @api.response(400, description="Registration was unsuccessful")
    @api.response(500, description="An internal server error occurred")
    @api.expect(Parsers.register, validate=True)
    def post(self):
        data = Parsers.register.parse_args()
        if User.exists_by_username(data["username"]):
            return {"message": "User with username equal to {} already exists".format(data["username"])}, 400
        new_user = User(username=data["username"],
                        password=User.generate_hash(data["password"]))
        try:
            db.session.add(new_user)
            db.session.commit()
            return {"success": True}, 200
        except Exception:
            return {"success": False}, 500


@api.route(schemas["users"])
class UsersQuery(Resource):
    @api.doc(security=security_grants)
    @require_oauth("profile")
    @api.response(200, description="List of users", model=Marshaller.users)
    @api.response(401, description="Unauthorized")
    def get(self):
        users = [UserBuilder(id, username) for id, username in db.session.query(User.id, User.username)]
        response = dict()
        response["users"] = users
        add_self(response, schemas["users"])
        return response


@api.route(schemas["user"].format(id="<user_id>"))
class ImagesQuery(Resource):
    @api.response(200, description="List of images of the selected user", model=Marshaller.user_images)
    @api.response(401, description="Unauthorized")
    @api.response(404, description="Selected user doesn't exist")
    @api.doc(security=security_grants)
    @require_oauth("profile")
    def get(self, user_id):
        if not User.exists_by_id(user_id):
            return {"message": "User with given name doesn't exist"}, 400
        selected_user = User.query.filter_by(id=user_id).first()
        selected_images = Image.query.filter_by(user_id=user_id).all()
        images = [ImageBuilder(user_id, image.id, image.guid, image.title) for image in selected_images]
        response = UserBuilder(user_id, selected_user.username)
        response["images"] = images
        add_self(response, schemas["user"].format(id=user_id))
        return response


@api.route(schemas["upload"])
class ImageUpload(Resource):
    @api.response(401, description="Unauthorized")
    @api.response(400, description="Upload wasn't successful")
    @api.response(200, description="Upload was successful")
    @api.doc(security=security_grants)
    @api.expect(Parsers.image_upload, validate=True)
    @require_oauth("profile")
    def post(self):
        user_id = current_token.user.id
        bucket = boto3.resource("s3").Bucket(config["bucket_name"])
        data = Parsers.image_upload.parse_args()
        new_guid = uuid.uuid4().hex
        new_image = Image(title=data["title"], user_id=user_id, guid=new_guid)
        new_file = data["image"].read()
        new_type = get_mimetype(new_file)
        if not check_size_type(new_type, new_file):
            return {"success": False}, 400
        try:
            bucket.put_object(Body=new_file, Key=new_guid, ContentType=new_type, ACL="public-read")
        except ClientError:
            return {"message": "Error uploading the image to the storage"}, 400
        try:
            db.session.add(new_image)
            db.session.commit()
        except SQLAlchemyError:
            boto3.resource("s3").Object(config["bucket_name"], new_guid).delete()
            return {"success": False}, 400
        return {"success": True}, 200


@api.route(schemas["image"].format(user_id="<user_id>", image_id="<image_id>"))
class ImageQuery(Resource):
    @api.response(200, description="Information about the selected image", model=Marshaller.single_image)
    @api.response(404, description="Selected image doesn't exist")
    @api.response(401, description="Unauthorized")
    @api.doc(security=security_grants)
    @require_oauth("profile")
    def get(self, user_id, image_id):
        image = Image.query.filter_by(id=image_id, user_id=user_id).first()
        if not image:
            return {"message": "Selected image doesn't exist"}, 404
        response = dict()
        response["id"] = image_id
        response["guid"] = image.guid
        response["title"] = image.title
        response["url"] = config["storage"].format(bucket_name=config["bucket_name"], guid=image.guid)
        add_self(response, schemas["image"].format(user_id=user_id, image_id=image_id))
        user_link = dict()
        user_link["href"] = schemas["user"].format(id=user_id)
        response["_links"]["user"] = user_link
        return response

    @api.response(200, description="Delete was successful")
    @api.response(404, description="Selected image doesn't exist")
    @api.response(400, description="An error occurred during the delete")
    @api.response(401, description="Unauthorized")
    @api.doc(security=security_grants)
    @require_oauth("profile")
    def delete(self, user_id, image_id):
        if user_id != str(current_token.user.id):
            return {"success": False}, 401
        image = Image.query.filter_by(id=image_id, user_id=user_id).first()
        if not image:
            return {"success": False}, 404
        # Delete S3 Object
        s3 = boto3.resource("s3")
        try:
            s3.Object(config["bucket_name"], image.guid).delete()
        except ClientError as e:
            return {"aws_error": e.response["Error"]["Code"]}, 400
        # Delete SQL Object
        Image.query.filter_by(id=image_id).delete()
        db.session.commit()
        return {"success": True}


@api.route(schemas["image"].format(user_id="<user_id>", image_id="<image_id>")+"/get")
class ImageStorage(Resource):
    @api.response(200, description="Redirect to the image file")
    @api.response(404, description="Selected image doesn't exist")
    @api.doc(security=security_grants)
    @require_oauth("profile")
    def get(self, user_id, image_id):
        image = Image.query.filter_by(id=image_id, user_id=user_id).first()
        if not image:
            return {"message": "Selected image doesn't exist"}, 400
        redirect(config["storage"].format(bucket_name=config["bucket_name"], guid=image.guid))
