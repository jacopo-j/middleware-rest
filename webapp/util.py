import time

from flask import session

import re
import uuid
import magic
import sys

from werkzeug.security import gen_salt

from webapp.api.model import User
from webapp.modules import schemas, config


def split_by_crlf(s):
    return [v for v in s.splitlines() if v]


def current_user():
    if 'id' in session:
        uid = session['id']
        return User.query.get(uid)
    return None


def add_self(object: dict, link):
    self_link = dict()
    self_link["href"] = link
    if "_links" not in object:
        object["_links"] = dict()
    object["_links"]["self"] = self_link


class UserBuilder(dict):
    def __init__(self, id, username):
        dict.__init__(self)
        self["id"] = id
        self["username"] = username
        add_self(self, schemas["user"].format(id=id))


class ImageBuilder(dict):
    def __init__(self, user_id, image_id, guid, title):
        dict.__init__(self)
        self["id"] = image_id
        self["title"] = title
        self["guid"] = guid
        add_self(self, schemas["image"].format(user_id=user_id, image_id=guid))


def check_size_type(new_type, data: bytes):
    image_pattern = re.compile("image/*")
    if not image_pattern.match(new_type):
        return False
    if sys.getsizeof(data) / 1000 > config['max_size_kb']:
        return False
    return True


def get_mimetype(data: bytes):
    f = magic.Magic(mime=True)
    return f.from_buffer(data)




