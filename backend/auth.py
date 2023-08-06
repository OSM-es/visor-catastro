import time
import urllib.parse

from authlib.jose import jwt
from authlib.jose.errors import JoseError
from authlib.integrations.flask_client import OAuth, OAuthError
from flask import Blueprint, abort, current_app, redirect, session, url_for
from flask_httpauth import HTTPTokenAuth
from sqlalchemy.exc import IntegrityError

from models import OsmUser, User, db

auth = HTTPTokenAuth(scheme="Bearer")
auth_bp = Blueprint('auth', __name__, url_prefix='/api')
oauth = OAuth()


def get_oauth():
    """Devuelve cliente OAuth2 configurado para OSM."""
    if not oauth.app:
        osm_url = current_app.config['OSM_URL']
        oauth.init_app(current_app)
        oauth.register(
            name='osm',
            access_token_url=osm_url + '/oauth2/token',
            authorize_url=osm_url + '/oauth2/authorize',
            api_base_url=osm_url + '/api/0.6/',
            client_kwargs={'scope': 'read_prefs'},
        )
    return oauth.osm

def passTutorial(user):
    user.tutorial = {'passed': ['login'], 'next': 'setup'}
    user.role = User.Role.MAPPER.value

def get_current_user():
    if 'user' in session:
        return OsmUser.query.get(session['user']['id'])
    return None


@auth.verify_token
def verify_token(token):
    """Verificador utilizado por auth.login_required"""
    try:
        s = jwt.decode(token, current_app.secret_key)
        s.validate()
    except JoseError:
        return None
    return get_current_user()

@auth.get_user_roles
def get_user_roles(user):
    if user.user:
        return [User.Role(user.user.role)]
    return []


@auth.login_required
@auth_bp.route('/relogin')
def relogin():
    """Redirige a la página de logout, luego a login de OSM."""
    r = login()
    session['user']['relogin'] = True
    session.modified = True
    url = (
        current_app.config['OSM_URL'] +
        '/logout?referer=' +
        urllib.parse.quote(r.location)
    )
    return redirect(url)

@auth_bp.route('/login')
def login():
    """Redirige a la página de login de OSM."""
    redirect_uri = url_for('auth.authorize', _external=True)
    if not current_app.debug:
        redirect_uri = redirect_uri.replace('http:', 'https:')
    return get_oauth().authorize_redirect(redirect_uri)

@auth_bp.route('/authorize')
def authorize():
    """Recibe el token de autorización de OSM.
    
    Lo guarda firmado en una cookie.
    Obtiene datos del usuario y los guarda en la sesión.
    Redirige a página auth del frontend.
    """
    try:
        token = get_oauth().authorize_access_token(verify=True)
    except OAuthError:
        abort(404, description="Autorización denegada")
    token['exp'] = time.time() + 864000
    resp = get_oauth().get('user/details.json')
    resp.raise_for_status()
    data = resp.json()

    id = data['user']['id']
    display_name=data['user']['display_name']
    img = data['user'].get('img', {}).get('href')
    osm_user = OsmUser.query.get(id)
    relogin = 'user' in session and session['user'].get('relogin', False)
    if relogin:
        last_user = OsmUser.query.get(session['user']['id'])
        user = last_user.user
    elif osm_user and osm_user.user:
        user = osm_user.user 
    else:
        user = User()
    if not osm_user:
        osm_user = OsmUser(id=id, display_name=display_name, img=img)
    if osm_user.isStated():
        user.import_user = osm_user
        passTutorial(user)
    elif relogin:
        if user.import_user:
            user.osm_user = osm_user
        elif user.osm_user:
            user.import_user = osm_user
        passTutorial(user)
    user.update_mapping_level(data['user']['changesets']['count'])
    if user.osm_user or user.import_user:
        db.session.add(user)
    db.session.add(osm_user)
    try:
        db.session.commit()
    except IntegrityError as e:
        print(str(e))
        abort(400, 'La cuenta que intentas vincular ya ha sido registrada, elimina una de ellas')

    if osm_user.user:
        data['user'].update(osm_user.user.asdict())
    s = jwt.encode({'alg': 'HS256'}, token, current_app.secret_key)
    data['user']['token'] = s.decode('utf-8')
    data['user']['stated'] = (
        osm_user.user and
        osm_user.user.import_user and
        osm_user.user.import_user.isStated()
    )
    session['user'] = data['user']
    session.modified = True
    session.permanent = True
    resp = redirect(current_app.config.get('CLIENT_URL', '') + '/auth')
    return resp

@auth_bp.route('/logout')
def logout():
    """Libera los datos del usuario almacenados en la sessión."""
    session.pop('user', None)
    return 'logged out'
