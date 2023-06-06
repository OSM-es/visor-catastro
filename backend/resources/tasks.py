import json
import gzip
import os

from flask import Response, abort, current_app, request
from flask_restful import Resource
import geopandas
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

def isAddr(feature):
    return 'addr' in '-'.join(feature['properties'].get('tags', {}).keys())

class Task(Resource):
    def get(self, id):
        task = models.Task.query.get(id)
        if not task:
            abort(404)
        fn = UPDATE + task.muncode + '/tasks/' + task.localId + '.osm.gz'
        with gzip.open(fn) as fo:
            xml = fo.read()
        geojson = osm2geojson.xml2geojson(xml, filter_used_refs=False)
        shapes = osm2geojson.xml2shapes(xml)
        filtered = []
        for f in geojson['features']:
            if 'tags' in f['properties']:
                if f['properties']['type'] != 'node' or isAddr(f):
                    filtered.append(f)
        buildings = [f for f in filtered if 'building:part' not in f['properties']['tags']]
        for s in shapes:
            if isAddr(s):
                node = s['shape'].point_on_surface()
                tags = s['properties']['tags']
                f = osm2geojson.shape_to_feature(node, {'type': 'node', 'tags': tags})
                buildings.append(f)
        parts = [f for f in filtered if 'building:part' in f['properties']['tags']]
        fn = UPDATE + task.muncode + '/tasks/' + task.localId + '.fixmes.geojson'
        data = task.asdict()
        if os.path.exists(fn):
            with open(fn) as fo:
                fixmes = json.load(fo)
            data['fixmes'] = fixmes
        data['buildings'] = {'type': geojson['type'], 'features': buildings}
        data['parts'] = {'type': geojson['type'], 'features': parts}
        return data
    
    def put(self, id):
        task = models.Task.query.get(id)
        if not task:
            abort(404)
        data = request.json
        task.status = data['status']
        models.db.session.commit()