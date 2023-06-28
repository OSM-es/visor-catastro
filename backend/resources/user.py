from flask import abort, request, session
from flask_restful import Resource

import models
from auth import auth, get_current_user


class User(Resource):
    @auth.login_required
    def post(self):
        osm_user = get_current_user()
        if osm_user.user:
            abort(400, 'La cuenta ya ha sido registrada')
        if request.json.get('type', '') == 'import':
            user = models.User(import_user=osm_user)
        else:
            user = models.User(osm_user=osm_user)
        models.db.session.add(user)
        models.db.session.commit()
        session['user'].update(user.asdict())
        session.modified = True
        return {'errors': []}

    @auth.login_required
    def put(self):
        osm_user = get_current_user()
        user = osm_user.user
        if not user:
            abort(400)
        user.email = request.json.get('email', None)
        models.db.session.add(user)
        models.db.session.commit()
        session['user'].update(user.asdict())
        session.modified = True
        return {'errors': []}
