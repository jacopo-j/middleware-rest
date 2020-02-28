from webapp import db, schemas


class UserBuilder(dict):
    def __init__(self, id, username):
        dict.__init__(self)
        self["id"] = id
        self["username"] = username
        self["_links"] = {}
        self.add_self()

    def add_self(self):
        self_link = dict()
        self_link["href"] = schemas["users"]
        self["_links"]["self"] = self_link


