from flask import Blueprint
from flask_restful import Api

import resources


api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp)
api.add_resource(resources.Status, '')
api.add_resource(resources.Provinces, '/provinces')
api.add_resource(resources.Municipalities, '/municipalities')
api.add_resource(resources.Streets, '/streets/<string:mun_code>')
api.add_resource(resources.Street, '/street/<string:mun_code>/<string:cat_name>')
api.add_resource(resources.Tasks, '/tasks')
api.add_resource(resources.Task, '/task/<int:id>')
api.add_resource(resources.User, '/user')