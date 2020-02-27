from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from passlib.hash import pbkdf2_sha256 as sha256
from . import db


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    image = relationship("Image")

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @classmethod
    def exists_by_id(cls, searched_id):
        return cls.query.filter_by(id=searched_id).count() != 0

class Image(db.Model):
    __tablename__ = 'images'
    key = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)


