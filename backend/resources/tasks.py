import gzip

from flask import Response, abort, request
from flask_restful import Resource
from shapely import bounds, buffer, GeometryCollection
import geopandas
import osm2geojson

import models
from auth import auth, get_current_user
from config import Config
from overpass import getOsmStreets

Municipality = models.Municipality
UPDATE = Config.UPDATE_PATH


class Tasks(Resource):
    def get(self):
        q = models.Task.query
        bounds = request.args.get('bounds', '').split(",")
        if len(bounds) == 4:
            bb = f"LINESTRING({bounds[0]} {bounds[1]}, {bounds[2]} {bounds[3]})"
            q = q.filter(models.Task.geom.intersects(bb))
        models.TaskLock.update_locks()
        sql = q.statement
        df = geopandas.GeoDataFrame.from_postgis(sql=sql, con=models.db.get_engine())
        get_status = lambda v: models.Task.Status(v).name
        get_diff = lambda v: models.Task.Difficulty(v).name
        df['difficulty'] = df['difficulty'].map(get_diff)
        df['status'] = df[['ad_status', 'bu_status']].max(axis=1).map(get_status)
        df['ad_status'] = df['ad_status'].map(get_status)
        df['bu_status'] = df['bu_status'].map(get_status)
        q = Municipality.query.filter(Municipality.muncode.in_(df.muncode.unique()))
        municip = {m.muncode: m.name for m in q.all()}
        df['name'] = df['muncode'].map(lambda v: municip[v])
        return Response(df.to_json(), mimetype='application/json')


class Task(Resource):
    def get(self, id):
        task = models.Task.query.get(id)
        if not task:
            abort(404)
        user = get_current_user()
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
        data['name'] = Municipality.get_by_code(task.muncode).name
        if fixmes: data['fixmes'] = {'type': geojson['type'], 'features': fixmes}
        data['buildings'] = {'type': geojson['type'], 'features': buildings}
        data['parts'] = {'type': geojson['type'], 'features': parts}
        data['osmStreets'] = osm2geojson.xml2geojson(getOsmStreets(bb))
        data['streets'] = get_streets(buildings)
        data['currentLock'] = user.user.lock.task.id if user and user.user and user.user.lock else None
        return data
    
    @auth.login_required(role=[models.User.Role.MAPPER, models.User.Role.ADMIN])
    def put(self, id):
        task = models.Task.query.get(id)
        if not task:
            abort(404)
        user = auth.current_user()
        data = request.json
        status = data.get('status')
        status = status and models.Task.Status[status]
        lock = data.get('lock')
        lock = lock and models.TaskLock.Action[lock]
        addresses = data.get('addresses') == 'true'
        buildings = data.get('buildings') == 'true'
        try:
            if lock == models.TaskLock.Action.UNLOCK:
                task.unlock(user)
            elif lock:
                task.set_lock(user, lock, buildings, addresses)
            else:
                task.change_status(user, status, buildings, addresses)
        except PermissionError:
            print('per')
            abort(403)
        except ValueError:
            print('val')
            abort(400)


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
