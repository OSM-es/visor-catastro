import datetime

from flask import request
from flask_restful import Resource
from geoalchemy2.shape import to_shape
import geopandas

import models
from resources.utils import json_compress


def convertDate(o):
    if isinstance(o, datetime.datetime):
        return o.strftime('%Y-%m-%d')

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
        get_mapped = lambda v: models.Task.query_mapped(models.Task.query_by_muncode(v)).count()
        get_centre = lambda v: (to_shape(v).y, to_shape(v).x)
        df['mapped_count'] = df['muncode'].map(get_mapped)
        df['centre'] = df['centre'].map(get_centre)
        data = df.to_json(default=convertDate).encode('utf-8')
        return data