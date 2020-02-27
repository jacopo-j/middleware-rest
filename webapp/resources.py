from flask_restful import Resource


class Index(Resource):

    def get(self):
        return "<h1>Hello World!</h1>"
