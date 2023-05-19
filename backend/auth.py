import time
from authlib.jose import jwt
from authlib.jose.errors import JoseError
from authlib.integrations.flask_client import OAuth, OAuthError
from flask import Blueprint, abort, current_app, redirect, session, url_for
from flask_httpauth import HTTPTokenAuth

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

@auth.verify_token
def verify_token(token):
    """Verificador utilizado por auth.login_required"""
    print('verify', token)
    try:
        s = jwt.decode(token, current_app.secret_key)
        print(s)
        s.validate()
        print('valid')
    except JoseError as e:
        return False
    return True

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
    resp = get_oauth().get('user/details.json')
    resp.raise_for_status()
    data = resp.json()
    session['user'] = data['user']
    session.modified = True
    session.permanent = True
    token['exp'] = time.time() + 864000
    s = jwt.encode({'alg': 'HS256'}, token, current_app.secret_key)
    resp = redirect(current_app.config.get('CLIENT_URL', '') + '/auth')
    resp.set_cookie('token', value=s, httponly=True, expires=token['exp'])
    return resp

@auth_bp.route('/logout')
def logout():
    """Libera los datos del usuario almacenados en la sessión."""
    session.pop('user', None)
    return {'logged out'}
