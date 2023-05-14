from flask import Blueprint
from flask_restful import Api

import resources


api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp)
api.add_resource(resources.Status, '')
api.add_resource(resources.Tasks, '/tasks')
api.add_resource(resources.User, '/user')