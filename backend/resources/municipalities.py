import datetime

from flask import Response, request
from flask_restful import Resource
import geopandas

import models
from config import Config


def convertDate(o):
    if isinstance(o, datetime.datetime):
        return o.strftime('%Y-%m-%d')

class Municipalities(Resource):
    def get(self):
        q = models.Municipality.query
        bounds = request.args.get('bounds', '').split(",")
        if len(bounds) == 4:
            bb = f"LINESTRING({bounds[0]} {bounds[1]}, {bounds[2]} {bounds[3]})"
            q = q.filter(models.Municipality.geom.intersects(bb))
        sql = q.statement
        df = geopandas.GeoDataFrame.from_postgis(sql=sql, con=models.db.get_engine())
        return Response(df.to_json(default=convertDate), mimetype='application/json')
