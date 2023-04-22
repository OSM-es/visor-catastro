"""
Microservicio de carga de actualización a la base de datos.

Registra los municipios creados en /data/update y sus tareas.
Transfiere a /data/dist.
"""
import json

from flask import Blueprint, current_app
import geojson
from shapely.geometry import shape
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon
from geoalchemy2.shape import from_shape

from models import db, Municipality, Task

UPLOAD = '/data/update/'
uploader = Blueprint('uploader', __name__, url_prefix='/')


def merge_tasks(mun_code):
    """Lee la zonificación de tareas.
    Agrega geometrías de tareas formada por geometrías múltiples.
    """
    filename = UPLOAD + mun_code + '/' + 'zoning.geojson'
    with open(filename) as fo:
        data = geojson.load(fo)
    tasks = {}
    for feat in data['features']:
        shp = shape(feat['geometry'])
        local_id = feat['properties']['localId']
        if local_id not in tasks:
            tasks[local_id] = feat
            tasks[local_id]['geometry'] = shp
        else:
            shp = tasks[local_id]['geometry'].union(shp)
            if isinstance(shp, Polygon):
               shp = MultiPolygon([shp])
            tasks[local_id]['geometry'] = shp
            tasks[local_id]['properties']['parts'] += feat['properties']['parts']
    return tasks


def load_tasks(tasks):
    """Registra las tareas.
    Por ahora sólo sirve para la carga inicial.
    TODO: Como pueden cambiar entre actualizaciones, 
    TODO: debe buscar si existe por la forma de la tarea, no
    TODO: por códigos. Falta el código para comprobar si hay diferencias.
    """
    new_tasks = 0
    for local_id, feat in tasks.items():
        mun_code = feat['properties']['muncode']
        task = Task.query.get((mun_code, local_id))
        if task is None:
            task = Task(**feat['properties'])
            task.geom = from_shape(feat['geometry'])
            db.session.add(task)
            new_tasks += 1
    db.session.commit()
    return new_tasks

@uploader.route("/<mun_code>")
def upload(mun_code):
    log = current_app.logger
    filename = UPLOAD + mun_code + '/' + 'report.json'
    with open(filename, 'r') as fo:
        report = json.load(fo)
    mun_name = report['mun_name']
    mun = Municipality.query.get(mun_code)
    if mun is None:
        mun = Municipality(muncode=mun_code, name=mun_name)
    elif mun.name != mun_name:
        mun.name = mun_name
    db.session.add(mun)
    db.session.commit()
    tasks = merge_tasks(mun_code)
    new_tasks = load_tasks(tasks)
    msg = f"Registradas {new_tasks} tareas nuevas de {len(tasks)} en {mun_code} {mun_name}"
    log.info(msg)
    return msg
