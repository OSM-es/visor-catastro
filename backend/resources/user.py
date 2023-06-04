from flask import abort, request, session
from flask_restful import Resource

import models
from auth import auth


class User(Resource):
    @auth.login_required
    def post(self):
        u = session.get('user')
        osm_user = models.OsmUser.query.get(u['id'])
        if osm_user.user:
            abort(400, 'La cuenta ya ha sido registrada')
        if request.json.get('type', '') == 'import':
            user = models.User(import_user=osm_user)
        else:
            user = models.User(osm_user=osm_user)
        models.db.session.add(user)
        models.db.session.commit()
        session['user']['user'] = user.asdict()
        session.modified = True
        return {'user': session['user']['user']}
