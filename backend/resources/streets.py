import json
import re
from collections import defaultdict

import osm2geojson
import shapely
from flask import request
from flask_restful import Resource
from geoalchemy2.shape import to_shape

import models
from config import Config
from overpass import getOsmStreets


def getStreet(tags):
    return tags.get('addr:street') or tags.get('addr:place') or ''


class Streets(Resource):
    def get(self, mun_code):
        mun = models.Municipality.get_by_code(mun_code)
        bounds = to_shape(mun.geom).bounds
        cat_name = request.args.get('name', '')
        streets = []
        for st in models.Street.query.filter(
            models.Street.mun_code == mun_code
        ).order_by(models.Street.source, models.Street.osm_name).all():
            streets.append(st.asdict())
            if not cat_name or cat_name == st.cat_name:
                cat_name = st.cat_name
                osm_name = st.osm_name
                source = st.source

        fn = Config.UPDATE_PATH + mun_code + '/tasks/address.osm'
        with open(fn) as fo:
            xml = fo.read()
        addresses = osm2geojson.xml2geojson(xml)
        addresses['features'] = [
            f for f in addresses['features']
            if f['properties'].get('tags', {}).get('addr:cat_name', '') == cat_name
        ]
        if (addresses['features']):
            shape = shapely.buffer(shapely.from_geojson(json.dumps(addresses)), 0.001)

            osm_streets = osm2geojson.xml2geojson(getOsmStreets(shape.bounds))

        data = {
            'mun_code': mun_code,
            'cat_name': cat_name,
            'osm_name': osm_name,
            'source': models.Street.Source(source).name,
            'bounds': bounds,
            'streets': streets,
            'addresses': addresses,
            'osmStreets': osm_streets,
        }

        return data
