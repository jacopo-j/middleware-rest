from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from passlib.hash import pbkdf2_sha256 as sha256
from .util import generate_guid
from . import db


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


class Image(db.Model):
    __tablename__ = 'images'
    id = db.Column(db.Integer, primary_key=True)
    guid = db.Column(db.String(32), nullable=False, unique=True, index=True, default=generate_guid)
    title = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)


