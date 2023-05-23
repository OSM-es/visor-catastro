from flask import Response, abort, current_app, request
from flask_restful import Resource
import geopandas
import gzip
import osm2geojson

import models
from config import Config

UPDATE = Config.UPDATE_PATH


class Tasks(Resource):
    def get(self):
        q = models.Task.query
        bounds = request.args.get('bounds', '').split(",")
        if len(bounds) == 4:
            bb = f"LINESTRING({bounds[0]} {bounds[1]}, {bounds[2]} {bounds[3]})"
            q = q.filter(models.Task.geom.intersects(bb))
        sql = q.statement
        df = geopandas.GeoDataFrame.from_postgis(sql=sql, con=models.db.get_engine())
        return Response(df.to_json(), mimetype='application/json')


class Task(Resource):
    def get(self, id):
        task = models.Task.query.get(id)
        if not task:
            abort(404)
        fn = UPDATE + task.muncode + '/tasks/' + task.localId + '.osm.gz'
        with gzip.open(fn) as fo:
            xml = fo.read()
        geojson = osm2geojson.xml2geojson(xml)
        data = task.asdict()
        data['content'] = geojson
        return data