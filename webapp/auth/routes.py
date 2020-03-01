import time

from flask import session
from flask_restplus import Resource
from werkzeug.security import gen_salt

from webapp.api.model import User
from webapp.auth.model import OAuth2Client
from webapp.modules import api, db, schemas
from webapp.auth.oauth2 import authorization
from webapp.parsers import Parsers
from webapp.util import current_user, split_by_crlf


@api.route(schemas["login"])
@api.doc(params={'username': 'Username', 'password': 'Password'})
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


@api.route(schemas["create_client"])
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


@api.route(schemas["authorize"])
class Authorize(Resource):
    def get(self):
        data = Parsers.authorize.parse_args()
        user = User.query.filter_by(id=data['user_id']).first()
        return authorization.create_authorization_response(grant_user=user)
    def post(self):
        data = Parsers.authorize.parse_args()
        user = User.query.filter_by(id=data['user_id']).first()
        return authorization.create_authorization_response(grant_user=user)


@api.route(schemas["issue_token"])
class IssueToken(Resource):
    def post(self):
        return authorization.create_token_response()


@api.route(schemas["revoke_token"])
class RevokeToken(Resource):
    def post(self):
        return authorization.create_endpoint_response('revocation')
