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
from geoalchemy2.shape import from_shape, to_shape

from models import db, Municipality, Task

UPLOAD = '/data/update/'
uploader = Blueprint('uploader', __name__, url_prefix='/')


def load_tasks(mun_code):
    """Registra las tareas.
    Una tarea puede estar formada por varias geometrías.
    Por ahora sólo sirve para la carga inicial.
    TODO: Como pueden cambiar entre actualizaciones, 
    TODO: debe buscar si existe por la forma de la tarea, no
    TODO: por códigos. Falta el código para comprobar si hay diferencias.
    """
    filename = UPLOAD + mun_code + '/' + 'zoning.geojson'
    with open(filename) as fo:
        data = geojson.load(fo)
    tasks = 0
    for feat in data['features']:
        shp = shape(feat['geometry'])
        local_id = feat['properties']['localId']
        task = Task.query.get((mun_code, local_id))
        if task is None:
            task = Task(**feat['properties'])
            task.geom = from_shape(shp)
            tasks += 1
        else:
            shp = to_shape(task.geom).union(shp)
            if isinstance(shp, Polygon):
               shp = MultiPolygon([shp])
            task.geom = from_shape(shp)
            task.parts += task.parts
        db.session.add(task)
    db.session.commit()
    return tasks

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
    tasks = load_tasks(mun_code)
    log.info(f"Registradas {tasks} tareas en {mun_code} {mun_name}")
    return f"Registradas {tasks} tareas en {mun_code} {mun_name}"
