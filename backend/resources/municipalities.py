import datetime

from flask import request, abort
from flask_restful import Resource
import geopandas

import models
from resources.utils import json_compress


def convertDate(o):
    if isinstance(o, datetime.datetime):
        return o.strftime('%Y-%m-%d')

def get_status(status):
    return lambda v: models.Task.query_status(
        models.Task.query_by_muncode(v), status
    ).count()

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
        sql = q.statement
        df = geopandas.GeoDataFrame.from_postgis(sql=sql, con=models.db.get_engine())
        df['validated_count'] = df['muncode'].map(get_status(models.Task.Status.VALIDATED))
        df['mapped_count'] = df['muncode'].map(get_status(models.Task.Status.MAPPED)) + df['validated_count']
        data = df.to_json(default=convertDate).encode('utf-8')
        return data

class Municipality(Resource):
    def get(self, code):
        mun = models.Municipality.get_by_code(code)
        if not mun:
            abort(404)
        return mun.asdict()