from flask import request, abort
from flask_restful import Resource

import models
from resources.utils import json_compress, get_proj_data


class Municipalities(Resource):
    @json_compress
    def get(self):
        q = models.Municipality.query
        code = request.args.get('code')
        if code and len(code) == 5:
            q = q.filter(models.Municipality.muncode == code)
        if code and len(code) == 2:
            q = models.Municipality.query_by_prov(code)
        bounds = request.args.get('bounds', '').split(",")
        if len(bounds) == 4:
            bb = f"LINESTRING({bounds[0]} {bounds[1]}, {bounds[2]} {bounds[3]})"
            q = q.filter(models.Municipality.geom.intersects(bb))
        return get_proj_data(q)

class Municipality(Resource):
    def get(self, code):
        mun = models.Municipality.get_by_code(code)
        if not mun:
            abort(404)
        return mun.asdict()