import gzip
import json

import osm2geojson
import shapely
from flask import abort, request
from flask_restful import Resource
from geoalchemy2.shape import to_shape

import models
from auth import auth, get_current_user
from overpass import getOsmStreets


def getStreet(tags):
    return tags.get('addr:street') or tags.get('addr:place') or ''


class Streets(Resource):
    def get(self, id, cat_name=None):
        task = models.Task.query.get(id)
        if not task: abort(404)
        mun_code = task.muncode
        municipality = models.Municipality.get_by_code(mun_code)

        with gzip.open(task.path()) as fo:
            xml = fo.read()
        geojson = osm2geojson.xml2geojson(xml, filter_used_refs=False)
        task_streets = {
            f['properties'].get('tags', {}).get('addr:cat_name', '')
            for f in geojson['features']
            if f['properties'].get('tags', {}).get('addr:cat_name', '')
        }
        if not cat_name and task_streets: cat_name = list(task_streets)[0]

        bounds = to_shape(municipality.geom).bounds
        streets = []
        street = None
        for st in models.Street.query.filter(
            models.Street.mun_code == mun_code
        ).order_by(
            models.Street.source, models.Street.osm_name
        ).all():
            streets.append(st.asdict())
            streets[-1]['in_task'] = st.cat_name in task_streets
            if not cat_name: cat_name = st.cat_name
            if cat_name == st.cat_name:
                cat_name = st.cat_name
                street = st
        if not street: abort(404)

        user = get_current_user()
        if street and not street.is_locked() and user:
            street.set_lock(user)

        fn = models.Task.get_path(mun_code, 'address.osm')
        with open(fn) as fo:
            xml = fo.read()
        addresses = osm2geojson.xml2geojson(xml)
        addresses['features'] = [
            f for f in addresses['features']
            if f['properties'].get('tags', {}).get('addr:cat_name', '') == cat_name
        ]
        shape = shapely.buffer(shapely.from_geojson(json.dumps(addresses)), 0.001)
        xml = getOsmStreets(shape.bounds)
        osm_streets = None
        if xml:
            osm_streets = osm2geojson.xml2geojson(xml)

        data = {
            'street': street.asdict(),
            'bounds': bounds,
            'streets': streets,
            'addresses': addresses,
            'osmStreets': osm_streets,
        }
        return data


class Street(Resource):
    @auth.login_required
    def put(self, mun_code, cat_name):
        data = request.json
        user = auth.current_user()
        street = models.Street.get_by_name(mun_code, cat_name)
        if not street:
            abort(404)
        if street.owner != user:
            abort(403)
        street.validated = data['validated'] == 'true'
        street.name = None if not street.validated else data.get('name')
        street.unlock()
        street.add_history(user)
        models.db.session.add(street)
        models.db.session.commit()
        return {'errors': []}


class StreetLock(Resource):
    @auth.login_required
    def delete(self, mun_code, cat_name):
        user = auth.current_user()
        street = models.Street.get_by_name(mun_code, cat_name)
        if street.owner == user:
            street.unlock()