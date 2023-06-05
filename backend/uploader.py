"""
Microservicio de carga de actualización a la base de datos.

Registra los municipios creados en /data/update y sus tareas.
Transfiere a /data/dist.
"""
import datetime
import json

import geojson
import osm2geojson
import requests
from flask import Blueprint, current_app, request
from shapely.geometry import shape
from shapely import GeometryCollection
from geoalchemy2.shape import from_shape

from models import db, Municipality, Province, Task
from config import Config

UPDATE = Config.UPDATE_PATH
uploader = Blueprint('uploader', __name__, url_prefix='/')


def get_geometry(url, level):
    """Busca una geometría en overpass."""
    response = requests.get(url)
    shapes = osm2geojson.xml2shapes(response.text)
    shape = [
        s for s in shapes 
        if s['properties']['tags'].get('admin_level', '') == level
    ][0]
    geom = GeometryCollection(shape['shape'])
    return shape, from_shape(geom)

def merge_tasks(zoning):
    """Lee la zonificación de tareas.
    Agrega geometrías de tareas formada por geometrías múltiples.
    """
    with open(zoning) as fo:
        data = geojson.load(fo)
    tasks = {}
    for feat in data['features']:
        shp = shape(feat['geometry'])
        local_id = feat['properties']['localId']
        if local_id not in tasks:
            tasks[local_id] = feat
            tasks[local_id]['geometry'] = GeometryCollection(shp)
        else:
            geoms = list(tasks[local_id]['geometry'].geoms)
            geoms.append(shp)
            tasks[local_id]['geometry'] = GeometryCollection(geoms)
            tasks[local_id]['properties']['parts'] += feat['properties']['parts']
    return tasks


def load_tasks(mun_code, tasks):
    """Registra las tareas.
    Por ahora no contempla estado, reemplaza todas las tareas.
    TODO: Como pueden cambiar entre actualizaciones, 
    TODO: debe buscar si existe por la forma de la tarea, no
    TODO: por códigos. Falta el código para comprobar si hay diferencias.
    """
    Task.query.filter(Task.muncode == mun_code).delete()
    for feat in tasks.values():
        task = Task(**feat['properties'])
        task.geom = from_shape(feat['geometry'])
        db.session.add(task)

@uploader.route("/")
def status():
    return "ok"

@uploader.route("/municipality/<mun_code>", methods=["PUT"])
def upload(mun_code):
    log = current_app.logger
    filename = UPDATE + mun_code + '/' + 'report.json'
    with open(filename, 'r') as fo:
        report = json.load(fo)
    mun_name = report['mun_name']
    src_date = datetime.date.fromisoformat(report['building_date'].replace('/', '-'))
    mun = Municipality.get_by_code(mun_code)
    if mun is None:
        mun = Municipality(muncode=mun_code, name=mun_name, date=src_date)
    elif mun.date == src_date:
        msg = f"{mun_code} ya está registrado"
        log.info(msg)
        return msg
    osmid = request.args.get('osmid', '')
    if osmid:
        url = (
            f'https://osm3s.cartobase.es/api/interpreter'
            f'?data=[out:xml][timeout:250];(wr({osmid}););(._;>>;);out meta;'
        )
        __, mun.geom = get_geometry(url, '8')
        log.info(f"Registrada geometría de {mun_code} {mun_name}")
    db.session.add(mun)
    zoning = UPDATE + mun_code + '/' + 'zoning.geojson'
    tasks = merge_tasks(zoning)
    load_tasks(mun_code, tasks)
    mun.name = mun_name
    mun.date = src_date
    db.session.commit()
    msg = f"Registradas {len(tasks)} tareas en {mun_code} {mun_name}"
    log.info(msg)
    return msg

@uploader.route("/province/<prov_code>", methods=["PUT"])
def province(prov_code):
    url = (
        f'https://osm3s.cartobase.es/api/interpreter'
        f'?data=[out:xml][timeout:250];(wr["boundary"="administrative"]'
        f'["ine:provincia"="{prov_code}"];);(._;>>;);out meta;'
    )
    shape, geom = get_geometry(url, '6')
    name = shape['properties']['tags']['name']
    prov = Province.get_by_code(prov_code)
    if prov is None:
        prov = Province(provcode=prov_code, name=name)
    prov.geom = geom
    db.session.add(prov)
    db.session.commit()
    msg = f"Registrada geometría de {prov_code} {name}"
    current_app.logger.info(msg)
    return msg
