"""
Microservicio de carga de actualización a la base de datos.

Registra los municipios creados en /data/update y sus tareas.
Transfiere a /data/dist.
"""
import json

from flask import Blueprint, current_app

UPLOAD = '/data/update/'
uploader = Blueprint('uploader', __name__, url_prefix='/')


@uploader.route("/<mun_code>")
def upload(mun_code):
    log = current_app.logger
    with open(UPLOAD + mun_code + '/' + 'report.json', 'r') as fo:
        report = json.load(fo)
    mun_name = report['mun_name']
    log.info(f"uploading {mun_code} {mun_name}!")
    return f"uploading {mun_code} {mun_name}!"
