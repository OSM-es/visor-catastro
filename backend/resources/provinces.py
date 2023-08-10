from flask import request
from flask_restful import Resource

import models
from resources.utils import json_compress, get_proj_data


def get_status(status):
    return lambda v: models.Task.query_status(
        models.Task.query_by_code(v), status
    ).count()

class Provinces(Resource):
    @json_compress
    def get(self):
        q = models.Province.query
        code = request.args.get('code')
        if code and len(code) == 2:
            q = q.filter(models.Province.provcode == code)
        bounds = request.args.get('bounds', '').split(",")
        if len(bounds) == 4:
            bb = f"LINESTRING({bounds[0]} {bounds[1]}, {bounds[2]} {bounds[3]})"
            q = q.filter(models.Province.geom.intersects(bb))        
        return get_proj_data(q, 'prov')
