import datetime
import json
import re
import gzip
from functools import wraps

import geopandas
from flask import Response
from shapely import GeometryCollection

import models


def json_compress(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = f(args[0])
        content = gzip.compress(data)
        response = Response(content, mimetype='application/json')
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    return decorated_function


def convertDate(o):
    if isinstance(o, datetime.datetime):
        return o.strftime('%Y-%m-%d')

def count_tasks(status):
    return lambda v: models.Task.query_status(
        models.Task.query_by_muncode(v), status
    ).count()

def get_status(f):
    status = models.Municipality.Status.READY
    if f.task_count == f.validated_count:
        status = models.Municipality.Status.VALIDATED
    elif f.task_count == f.mapped_count:
        status = models.Municipality.Status.MAPPED
    elif f.mapped_count > 0:
        status = models.Municipality.Status.MAPPING
    return status.name

def get_proj_data(query, proj='mun'):
    sql = query.statement
    df = geopandas.GeoDataFrame.from_postgis(sql=sql, con=models.db.get_engine())
    geoms = []
    df.geom.map(lambda v: geoms.append(v))
    bb = GeometryCollection(geoms).bounds
    bounds = [[bb[3], bb[2]], [bb[1], bb[0]]]
    df['validated_count'] = df[proj + 'code'].map(count_tasks(models.Task.Status.VALIDATED))
    df['mapped_count'] = df[proj + 'code'].map(count_tasks(models.Task.Status.MAPPED)) + df['validated_count']
    df['status'] = df.apply(get_status, axis=1)
    data = df.to_json(default=convertDate)
    data = re.sub(r'\}$', f', "bounds": "{json.dumps(bounds)}"}}', data)
    return data.encode('utf-8')
