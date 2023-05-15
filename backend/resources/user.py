from flask import session
from flask_restful import Resource

from auth import auth


class User(Resource):
    def get(self):
        user = session.get('user')
        return user
