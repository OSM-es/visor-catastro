from flask import abort, request
from flask_restful import Resource

import models
from auth import auth


class Fixme(Resource):
    @auth.login_required(role=[models.User.Role.MAPPER, models.User.Role.ADMIN])
    def put(self, id):
        fixme = models.Fixme.query.get(id)
        if not fixme:
            abort(404)
        data = request.json
        try:
            fixme.validated = 'validated' in data
            models.db.session.commit()
        except PermissionError:
            abort(403)
