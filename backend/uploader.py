"""
Microservicio de carga de actualización a la base de datos.

Registra los municipios creados en /data/update y sus tareas.
Transfiere a /data/dist.
"""
import datetime
import json

import csv
import geojson
import gzip
import osm2geojson
import requests
from flask import Blueprint, abort, current_app, request
from shapely.geometry import shape
from shapely import GeometryCollection
from geoalchemy2.shape import from_shape

import overpass
from models import db, Municipality, Province, Street, Task
from config import Config

MODERATE_THRESHOLD = 10
CHALLENGING_THRESHOLD = 20
UPDATE = Config.UPDATE_PATH
uploader = Blueprint('uploader', __name__, url_prefix='/')


def get_geometry(*ql, search=None, level=6):
    """Busca geometría de límite administrativo en overpass."""
    text = overpass.query(*ql, search=search)
    if not text:
        abort(500)
    shapes = osm2geojson.xml2shapes(text)
    shape = [
        s for s in shapes 
        if s['properties'].get('tags', {}).get('admin_level', '') == level
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

def calc_difficulty(task):
    """Obtiene los datos necesarios para calcular la dificultad."""
    fn = f"{UPDATE}{task.muncode}/tasks/{task.localId}.osm.gz"
    with gzip.open(fn) as fo:
        xml = fo.read()
    geojson = osm2geojson.xml2geojson(xml)
    (buildings, parts, addresses) = (0, 0, 0)
    for feat in geojson['features']:
        tags = feat['properties'].get('tags', {})
        buildings += 1 if 'building' in tags else 0
        parts += 1 if 'building:part' in tags else 0
        addresses += 1 if 'addr:cat_name' in tags else 0
    complexity = max(buildings, parts, addresses)
    if complexity >= CHALLENGING_THRESHOLD:
        difficulty = Task.Difficulty['CHALLENGING']
    elif complexity >= MODERATE_THRESHOLD:
        difficulty = Task.Difficulty['MODERATE']
    else:
        difficulty = Task.Difficulty['EASY']
    task.buildings = buildings
    task.parts = parts
    task.addresses = addresses
    task.difficulty = difficulty.value

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
        calc_difficulty(task)
        db.session.add(task)

def upload_streets(mun_code):
    """Registra el callejero del municipio.
    
    Excluye las calles que no tengan ninguna dirección asociada.
    """
    fn = UPDATE + mun_code + '/tasks/address.osm'
    with open(fn) as fh:
        xml = fh.read()
    data = osm2geojson.xml2geojson(xml)
    addresses = {
        ad['properties'].get('tags', {}).get('addr:cat_name', '')
        for ad in data['features']
    }
    fn = UPDATE + mun_code + '/tasks/highway_names.csv'
    count = 0
    with open(fn) as fh:
        for st in csv.reader(fh, delimiter='\t'):
            cat_name, osm_name, source = st[0:3]
            if osm_name and cat_name in addresses:
                street = Street(
                    mun_code=mun_code,
                    cat_name=cat_name,
                    osm_name=osm_name,
                    source=Street.Source[source].value
                )
                db.session.add(street)
                count += 1
    db.session.commit()
    msg = f"Registradas {count} calles en {mun_code}"
    current_app.logger.info(msg)

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
        __, mun.geom = get_geometry('wr', search=osmid, level='8')
        log.info(f"Registrada geometría de {mun_code} {mun_name}")
    db.session.add(mun)
    zoning = UPDATE + mun_code + '/' + 'zoning.geojson'
    tasks = merge_tasks(zoning)
    load_tasks(mun_code, tasks)
    mun.name = mun_name
    mun.date = src_date
    db.session.commit()
    msg = f"Registradas {len(tasks)} tareas en {mun_code} {mun_name}"
    upload_streets(mun_code)
    log.info(msg)
    return msg

@uploader.route("/province/<prov_code>", methods=["PUT"])
def province(prov_code):
    ql = f'wr["boundary"="administrative"]["ine:provincia"="{prov_code}"]'
    shape, geom = get_geometry(ql, level='6')
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
