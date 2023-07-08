from email_validator import validate_email, EmailNotValidError
from flask import abort, request, session
from flask_restful import Resource

import models
from auth import auth


class User(Resource):
    @auth.login_required
    def post(self):
        osm_user = auth.current_user()
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
        return {}

    @auth.login_required
    def put(self):
        osm_user = auth.current_user()
        user = osm_user.user
        if not user:
            abort(400)
        email = request.json.get('email', None)
        try:
            emailinfo = validate_email(email, check_deliverability=False)
        except EmailNotValidError as e:
            print(str(e))
            return({'errors': {'email': str(e)}})
        user.email = emailinfo.normalized
        models.db.session.add(user)
        models.db.session.commit()
        session['user'].update(user.asdict())
        session.modified = True
        return {}
