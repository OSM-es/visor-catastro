"""
Microservicio de carga de actualización a la base de datos.

Registra los municipios creados en /data/update y sus tareas.
Transfiere a /data/dist.
"""
import datetime
import json
import shutil

import csv
import geojson
import gzip
import osm2geojson
from flask import Blueprint, abort, current_app
from shapely.geometry import shape
from shapely import GeometryCollection
from geoalchemy2.shape import from_shape

import overpass
from models import db, Municipality, Province, Street, Task
from config import Config
from diff import Diff

UPDATE = Config.UPDATE_PATH
DIST = Config.DIST_PATH
uploader = Blueprint('uploader', __name__, url_prefix='/')


@uploader.route("/")
def status():
    return "ok"

@uploader.route("/municipality/", methods=["PUT"])
def end_upload():
    log = current_app.logger
    log.info("Fin de actualización")
    s = Municipality.query.filter(Municipality.update_id is None).delete()
    for u in Municipality.Update.query.all():
        if u.muncode:
            u.do_update()
        else:
            db.session.delete(u.municipality)
            s += 1
    if s:
        log.info('Municipios eliminados: %s', s)
    Municipality.Update.query.delete()
    db.session.commit()
    return {}

@uploader.route("/municipality/<mun_code>", methods=["PUT"])
def upload(mun_code):
    log = current_app.logger
    filename = UPDATE + mun_code + '/' + 'report.json'
    with open(filename, 'r') as fo:
        report = json.load(fo)
    mun_name = report['mun_name']
    src_date = datetime.date.fromisoformat(report['building_date'].replace('/', '-'))
    mun_shape = get_mun_limits(mun_code)
    # TODO: Mantener un historial de cambios de geometría o nombre
    mun, candidates = Municipality.get_match(mun_code, mun_name, src_date, mun_shape)
    if candidates:
        if mun.src_date == src_date:
            return exit(f"{mun_code} ya está registrado")
        locks = [m.set_lock() for m in candidates]
        if not all(locks):
            return exit("No se han podido bloquear todos los municipios")
        mun.update.set(mun_code, mun_name, src_date, mun_shape)
    zoning = UPDATE + mun_code + '/' + 'zoning.geojson'
    tasks = merge_tasks(zoning)
    load_tasks(mun_code, tasks.values(), mun_shape)
    #load_tasks(mun_code, [tasks['6114001XJ2461S'], tasks['6114003XJ2461S']])
    log.info(f"Registradas {len(tasks)} tareas en {mun_code} {mun_name}")
    #upload_streets(mun_code)
    # shutil.move(UPDATE + mun_code, DIST + mun_code)
    if len(candidates) == 1 and mun.equal(mun_shape):
        mun.update.do_update()
    db.session.commit()
    return mun_code

@uploader.route("/province/<prov_code>", methods=["PUT"])
def province(prov_code):
    if prov_code in ['55', '56']:  # Ceuta y Melilla
        prov_code = str(int(prov_code) - 4)
        ql = f'wr["boundary"="administrative"]["ine:provincia"="{prov_code}"]'
        shape, geom = get_geometry(ql, level='4')
    else:
        ql = f'wr["boundary"="administrative"]["ine:provincia"="{prov_code}"]'
        shape, geom = get_geometry(ql, level='6')
    name = shape['properties']['tags']['name']
    prov = Province.get_by_code(prov_code)
    if prov is None:
        prov = Province(provcode=prov_code, name=name)
    prov.geom = geom
    db.session.add(prov)
    db.session.commit()
    return exit(f"Registrada geometría de {prov_code} {name}")


def exit(msg):
    current_app.logger.info(msg)
    return msg

def get_geometry(*ql, search=None, level=6):
    """Busca geometría de límite administrativo en overpass."""
    text = overpass.query(*ql, search=search)
    if not text:
        abort(500)
    shapes = osm2geojson.xml2shapes(text)
    shapes = [
        s for s in shapes 
        if s['properties'].get('tags', {}).get('admin_level', '') == level
    ]
    if not shapes:
        abort(500)
    shape = shapes[0]
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
    difficulty = Task.Difficulty.get_from_complexity(buildings, parts, addresses)
    task.buildings = buildings
    task.parts = parts
    task.addresses = addresses
    task.difficulty = difficulty.value

def load_tasks(mun_code, tasks, mun_shape):
    """Registra las tareas."""
    mun_geom = from_shape(mun_shape)
    old_tasks = [
        t.id for t in Task.query.filter(Task.geom.contained(mun_geom)).all()
    ]
    demolished = []
    for feat in tasks:
        task = Task(**feat['properties'])
        if task.type == 'R&uacute;stica': task.type = 'Rústica'
        geom = feat['geometry']
        task.geom = from_shape(geom)
        calc_difficulty(task)
        candidates = Task.get_by_area(task.geom)
        print(mun_code, len(candidates))
        if not candidates:
            db.session.add(task)
            continue
        diff = Diff(demolished=demolished)
        fn = Diff.get_filename(UPDATE, mun_code, task.localId)
        data = Diff.get_shapes(fn)
        Diff.shapes_to_dataframe(diff.df2, data, mun_code, task.localId, task.id)
        diff.clean_demolished()
        for c in candidates:
            if c.id in old_tasks: old_tasks.remove(c.id)
            fn = Diff.get_filename(DIST, c.muncode, c.localId)
            for feat in Diff.get_shapes(fn):
                geom = feat['shape']
                # shapely.errors.GEOSException: TopologyException: side location conflict at -1.5376820875309667 39.212811681255161. This can occur if the input geometry is invalid.
                # task_geom = to_shape(task.geom).buffer(0)
                if (
                    True or
                    c.ad_status != Task.Status.READY.value
                    or c.bu_status != Task.Status.READY.value
                ):
                    Diff.add_row(diff.df1, c.muncode, c.localId, c.id, feat)
        if len(diff.df1.index):
            diff.get_fixmes()
        #     for f in diff.fixmes:
        #         print(f['node'], f['task'], f['fixme'])
        #     print('----------------------')
        #     print(len(diff.demolished))
        #     for f in diff.demolished:
        #         print(f['node'], f['task'], f['fixme'])
        # si old no es vacio, ejecutar
        # mover
        # recorrer fixmes
        #   
        # agregar fixmes a bd
    if old_tasks:
        current_app.logger.info(f"Eliminadas {len(old_tasks)} tareas")
    for id in old_tasks:
        db.session.delete(Task.query.get(id))
    # agregar los fixmes de lo que queda en demolished

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

def get_mun_limits(mun_code):
    """Lee el archivo con la geometría del municipio."""
    fn = UPDATE + mun_code + '/' + mun_code + '.geojson'
    with open(fn) as fo:
        data = json.load(fo)
    geoms = [shape(feat['geometry']) for feat in data['features']]
    mun_geom = GeometryCollection(geoms)
    return mun_geom
 