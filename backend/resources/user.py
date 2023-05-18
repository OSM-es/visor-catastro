from flask import request, session
from flask_restful import Resource

from auth import auth


class User(Resource):
    def get(self):
        user = session.get('user')
        return user

    @auth.login_required
    def post(self):
        print(request.json)
        return 'ok'