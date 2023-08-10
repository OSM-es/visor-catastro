from flask import request
from flask_restful import Resource
import geopandas

import models
from resources.utils import json_compress


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
        sql = q.statement
        df = geopandas.GeoDataFrame.from_postgis(sql=sql, con=models.db.get_engine())
        df['validated_count'] = df['provcode'].map(get_status(models.Task.Status.VALIDATED))
        df['mapped_count'] = df['provcode'].map(get_status(models.Task.Status.MAPPED)) + df['validated_count']
        data = df.to_json().encode('utf-8')
        return data
