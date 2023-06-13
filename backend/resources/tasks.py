from collections import defaultdict
import gzip
import re

from flask import Response, abort, request
from flask_restful import Resource
from shapely import bounds, buffer, GeometryCollection
import geopandas
import osm2geojson

import overpass
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


def getStreets(boundingBox):
    bb = f'{boundingBox[1]},{boundingBox[0]},{boundingBox[3]},{boundingBox[2]}'
    ql = [
        'way["highway"]["name"]',
        'relation["highway"]["name"]',
        'way["place"="square"]["name"]',
        'relation["place"="square"]["name"]',
    ]
    text = overpass.query(*ql, search=bb)
    return osm2geojson.xml2geojson(text)

def isAddr(feature):
    return 'addr' in '-'.join(feature['properties'].get('tags', {}).keys())

def getStreet(tags):
    return tags.get('addr:street') or tags.get('addr:place') or ''

def get_osm_street_names(streets):
    return list({
        f['properties'].get('tags', {}).get('name')
        for f in streets['features']
        if f['properties'].get('tags', {}).get('name')
    })

def get_street_names(buildings, osmStreetNames):
    return list({
        getStreet(f['properties'].get('tags'))
        for f in buildings
        if getStreet(f['properties'].get('tags'))
    }.union(osmStreetNames))

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

def get_images(buildings):
    images = defaultdict(set)
    for f in buildings:
        tags = f['properties'].get('tags', {})
        if 'ref' in tags:
            ref = tags['ref']
            number = tags.get('addr:housenumber')
            try:
                number = number and f'{int(number):05}'
            except ValueError:
                pass
            street = getStreet(tags) + f', {number}' if number else ''
            if ref in images:
                if street: images[ref].add(street)
            else:
                images[ref] = {street} if street else {}
    data = [{'ref': ref, 'addrs': '; '.join(addrs)} for ref, addrs in images.items()]
    data.sort(key=lambda im: im['addrs'])
    for im in data:
        im['addrs'] = re.sub(r', 0+', ', ', im['addrs'])
    return data


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
        data['streets'] = getStreets(bb)
        data['osmStreetNames'] = get_osm_street_names(data['streets'])
        data['streetNames'] = get_street_names(buildings, data['osmStreetNames'])
        data['images'] = get_images(buildings)
        return data
    
    def put(self, id):
        task = models.Task.query.get(id)
        if not task:
            abort(404)
        data = request.json
        task.status = data['status']
        models.db.session.commit()