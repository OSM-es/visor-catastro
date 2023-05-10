from requests_oauthlib import OAuth2Session

from flask import current_app


OSM_ID = current_app.config['OSM_ID']
OSM_SECRET = current_app.config['OSM_SECRET']
osm_url = 'https://www.openstreetmap.org'
user_details_url = osm_url + '/api/0.6/user/details.json'
auth_url = osm_url + '/oauth2/authorize'
token_url = osm_url + '/oauth2/token'
scope = ['read_prefs']
oauth = OAuth2Session(OSM_ID, scope=scope)


def get_authorize_url(redirect_uri):
    oauth.redirect_uri = redirect_uri
    authorization_url, state = oauth.authorization_url(auth_url)
    return authorization_url

def authorize(authorization_response):
    token = oauth.fetch_token(
        token_url,
        authorization_response=authorization_response,
        client_secret=OSM_SECRET
    )
    return token

def logout():
    oauth.token = {}

def get_user_details():
    r = oauth.get(user_details_url)
    if r.ok:
        return r.json()