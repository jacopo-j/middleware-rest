from flask_restx import fields, Namespace

# Define the Namespace for user related routes
api = Namespace("users", description="Users related operations")


class Marshaller:
    self = api.model("Self", {
        "href": fields.String
    })

    user_link = api.model("User Link", {
        "href": fields.String
    })

    links = api.model("Links", {
        "self": fields.Nested(self, skip_none=True)
    })

    user = api.model("User", {
        "id": fields.Integer,
        "username": fields.String,
        "_links": fields.Nested(links, skip_none=True)
    })

    users = api.model("Users", {
        "users": fields.List(fields.Nested(user, skip_none=True)),
        "_links": fields.Nested(links, skip_none=True)
    })

    image = api.model("Image", {
        "id": fields.Integer,
        "title": fields.String,
        "guid": fields.String,
        "_links": fields.Nested(links, skip_none=True)
    })

    user_images = api.clone("User images", user, {
        "images": fields.List(fields.Nested(image, skip_none=True))
    })

    links_image = api.clone("Links Image", links, {
        "user": fields.Nested(user_link, skip_none=True)
    })

    single_image = api.clone("Single Image", image, {
        "url": fields.String,
        "_links": fields.Nested(links_image, skip_none=True)
    })


