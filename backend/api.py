import requests

from flask import Blueprint, Response, current_app
from flask_caching import Cache
from flask_restful import Api

import resources


api_bp = Blueprint('api', __name__, url_prefix='/api')
api_cache = Cache()
api = Api(api_bp)
api.add_resource(resources.Status, '')
api.add_resource(resources.Municipalities, '/municipalities')
api.add_resource(resources.Provinces, '/provinces')
api.add_resource(resources.Streets, '/task/<int:id>/street/<string:cat_name>')
api.add_resource(resources.Street, '/street/<string:mun_code>/<string:cat_name>')
api.add_resource(resources.StreetLock, '/street/<string:mun_code>/<string:cat_name>/lock')
api.add_resource(resources.Tasks, '/tasks')
api.add_resource(resources.Task, '/task/<int:id>')
api.add_resource(resources.User, '/user')


@api_bp.route('/photo/<string:ref>')
@api_cache.cached()
def getPhoto(ref):
    resp = False
    try:
        url = current_app.config.get('FOTO_FACHADA_URL') + ref
        resp = requests.get(url, stream=True)
    except requests.RequestException:
        resp = False
    if resp and resp.ok and int(resp.headers['Content-Length']) > 0:
        contentType = resp.headers['content-type']
        data = resp.raw.read()
    else:
        contentType = 'image/png'
        data = open('assets/noimage.png', 'rb').read()
    return Response(data, mimetype=contentType)

