from flask import Blueprint
from flask_restful import Api

from resources import Status, Tasks


api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp)
api.add_resource(Status, '/')
api.add_resource(Tasks, '/tasks')