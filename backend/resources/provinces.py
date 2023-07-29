from flask import request
from flask_restful import Resource
from geoalchemy2.shape import to_shape
import geopandas

import models
from resources.utils import json_compress


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
        get_mapped = lambda v: models.Task.query_mapped(models.Task.query_by_provcode(v)).count()
        get_centre = lambda v: (to_shape(v).y, to_shape(v).x)
        df['mapped_count'] = df['provcode'].map(get_mapped)
        df['centre'] = df['centre'].map(get_centre)
        data = df.to_json().encode('utf-8')
        return data
