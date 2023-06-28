import gzip

from flask import Response, abort, request
from flask_restful import Resource
from shapely import bounds, buffer, GeometryCollection
import geopandas
import osm2geojson

import models
from auth import auth
from config import Config
from overpass import getOsmStreets

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
        df['difficulty'] = df['difficulty'].map(lambda v: models.Task.Difficulty(v).name)
        df['status'] = df['status'].map(lambda v: models.Task.Status(v).name)
        Municipality = models.Municipality
        q = Municipality.query.filter(Municipality.muncode.in_(df.muncode.unique()))
        municip = {m.muncode: m.name for m in q.all()}
        df['name'] = df['muncode'].map(lambda v: municip[v])
        return Response(df.to_json(), mimetype='application/json')


def isAddr(feature):
    return 'addr' in '-'.join(feature['properties'].get('tags', {}).keys())

def getStreet(tags):
    return tags.get('addr:street') or tags.get('addr:place') or ''

def get_streets(buildings):
    names = {
        f['properties'].get('tags', {}).get('addr:cat_name', '')
        for f in buildings
        if f['properties'].get('tags', {}).get('addr:cat_name', '')
    }
    return [
        st.asdict()
        for st in models.Street.query.filter(
            models.Street.cat_name.in_(names)
        ).order_by(models.Street.source, models.Street.osm_name).all()
    ]

def remove_no_addr_nodes(geojson):
    filtered = []
    for f in geojson['features']:
        if 'tags' in f['properties']:
            if f['properties']['type'] != 'node' or isAddr(f):
                filtered.append(f)
    return filtered

def get_buildings_and_nodes_for_addr_in_areas(geojson, shapes):
    buildings = [f for f in geojson if 'building:part' not in f['properties']['tags']]
    for s in shapes:
        if isAddr(s):
            node = s['shape'].point_on_surface()
            tags = s['properties']['tags']
            f = osm2geojson.shape_to_feature(node, {'type': 'node', 'tags': tags})
            buildings.append(f)
    return buildings

def get_fixmes(shapes):
    fixmes = []
    for s in shapes:
        fixme = s['properties'].get('tags', {}).get('fixme')
        if fixme:
            node = s['shape'].point_on_surface()
            f = osm2geojson.shape_to_feature(node, {'fixme': fixme})
            fixmes.append(f)
    return fixmes


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
        bb = bounds(buffer(GeometryCollection([s['shape'] for s in shapes]), 0.001)).tolist()
        filtered = remove_no_addr_nodes(geojson)
        buildings = get_buildings_and_nodes_for_addr_in_areas(filtered, shapes)
        parts = [f for f in filtered if 'building:part' in f['properties']['tags']]
        fixmes = get_fixmes(shapes)
        fn = UPDATE + task.muncode + '/tasks/' + task.localId + '.fixmes.geojson'
        data = task.asdict()
        if fixmes: data['fixmes'] = {'type': geojson['type'], 'features': fixmes}
        data['buildings'] = {'type': geojson['type'], 'features': buildings}
        data['parts'] = {'type': geojson['type'], 'features': parts}
        data['osmStreets'] = osm2geojson.xml2geojson(getOsmStreets(bb))
        data['streets'] = get_streets(buildings)
        return data
    
    @auth.login_required(role=[models.User.Role.MAPPER, models.User.Role.ADMIN])
    def put(self, id):
        task = models.Task.query.get(id)
        if not task:
            abort(404)
        data = request.json
        task.status = models.Task.Status[data['status']].value
        models.db.session.commit()