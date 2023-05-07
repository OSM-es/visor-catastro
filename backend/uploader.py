"""
Microservicio de carga de actualización a la base de datos.

Registra los municipios creados en /data/update y sus tareas.
Transfiere a /data/dist.
"""
import datetime
import json

from flask import Blueprint, current_app
import geojson
from shapely.geometry import shape
from shapely import MultiPolygon, Polygon, GeometryCollection
from geoalchemy2.shape import from_shape

from models import db, Municipality, Task

UPDATE = '/data/update/'
uploader = Blueprint('uploader', __name__, url_prefix='/')


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
            tasks[local_id]['geometry'] = shp
        else:
            shp = tasks[local_id]['geometry'].union(shp)
            if isinstance(shp, Polygon):
                shp = MultiPolygon([shp])
            elif isinstance(shp, GeometryCollection):
                geoms = [g for g in shp.geoms if isinstance(shp, Polygon)]
                shp = MultiPolygon(geoms)
            tasks[local_id]['geometry'] = shp
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
