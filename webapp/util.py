from webapp import db, schemas
import uuid


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
