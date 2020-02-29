from webapp import schemas,config
import re
import uuid
import magic
import sys


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


def generate_guid():
    return uuid.uuid4().hex


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
