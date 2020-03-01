from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from passlib.hash import pbkdf2_sha256 as sha256
from flask_sqlalchemy import SQLAlchemy
import time
import uuid
from authlib.integrations.sqla_oauth2 import (
    OAuth2ClientMixin,
    OAuth2AuthorizationCodeMixin,
    OAuth2TokenMixin,
)


db = SQLAlchemy()


class OAuth2Client(db.Model, OAuth2ClientMixin):
    __tablename__ = 'oauth2_client'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User')


class OAuth2AuthorizationCode(db.Model, OAuth2AuthorizationCodeMixin):
    __tablename__ = 'oauth2_code'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User')


class OAuth2Token(db.Model, OAuth2TokenMixin):
    __tablename__ = 'oauth2_token'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    user = db.relationship('User')

    def is_refresh_token_active(self):
        if self.revoked:
            return False
        expires_at = self.issued_at + self.expires_in * 2
        return expires_at >= time.time()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), nullable=False, unique=True, index=True)
    password = db.Column(db.String(120), nullable=False)
    images = relationship("Image")

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @classmethod
    def exists_by_id(cls, searched_id):
        return cls.query.filter_by(id=searched_id).count() != 0

    @classmethod
    def exists_by_username(cls, searched_username):
        return cls.query.filter_by(username=searched_username).count() != 0

    def get_user_id(self):
        return self.id

def generate_guid():
    return uuid.uuid4().hex


class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String(32), nullable=False, unique=True, index=True, default=generate_guid)
    title = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)


