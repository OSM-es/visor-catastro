"""
Servicio para convertir archivos de Catastro a OSM.
Realiza la descarga inicial y la actualiza con las publicaciones períodicas.

Sube los datos a $CATASTRO_DATA/update

Registra la fecha origen de los datos de Catastro en src_date.txt
Los municipios procesados en municipios.json

Configuración: config.yaml
"""
import argparse
import json
import logging
import os
import re
import requests
import shutil
import schedule
import time
import yaml
from multiprocessing import Pool, current_process
from requests.exceptions import RequestException
from zipfile import BadZipfile

from catatom2osm import catatom
from catatom2osm import config as catconfig
from catatom2osm.app import CatAtom2Osm, QgsSingleton
from catatom2osm.boundary import get_municipalities
from catatom2osm.exceptions import CatException


class Config:
    def __init__(self):
        self.read_list('INCLUDE_MUNS')
        self.read_list('EXCLUDE_MUNS')
        self.read_list('INCLUDE_PROVS')
        for mun in self.include_muns + self.exclude_muns:
            if mun[0:2] not in self.include_provs:
                self.include_provs.append(mun[0:2])
        if not self.include_provs:
            self.include_provs = list(catconfig.prov_codes.keys())
        self.read_list('EXCLUDE_PROVS')
        self.read_value('UPLOADER_URL', 'http://uploader:5002/')
        self.read_list('CA_PROVS', '03, 07, 08, 12, 17, 25, 43, 46')
        self.read_list('GL_PROVS', '15, 27, 32, 36')
        self.read_value('CHECK_TIME', '00:13')
        self.read_int('WORKERS', 4)
        self.read_int('MAX_RETRIES', 10)
        self.read_int('RETRAY_DELAY', 3)

    def read_int(self, key, default):
        self.__dict__[key.lower()] = int(os.getenv(key, default))

    def read_value(self, key, default):
        self.__dict__[key.lower()] = os.getenv(key, default)
 
    def read_list(self, key, default=''):
        value = re.split(r', *', os.getenv(key, default))
        value = [] if value == [''] else value
        self.__dict__[key.lower()] = value

config = Config()

options = argparse.Namespace(
    path = [],
    args = "",
    address=True,
    building=True,
    comment=False,
    config_file=False,
    download=False,
    generate_config=False,
    info=False,
    log_level='INFO',
    list='',
    manual=False,
    parcel=[],
    split=None,
    zoning=False,
)


@schedule.repeat(schedule.every().day.at(config.check_time))
def daily_check():
    "Proceso de recogida de municipios con periodicidad diaria."
    municipios = {}
    provincias = config.include_provs
    retries = 0
    need_update = True
    catconfig.set_config({
        'show_progress_bars': False,
        'report_system_info': False,
    })
    while need_update and provincias and retries < config.max_retries:
        try:
            prov = provincias[0]
            if prov not in config.exclude_provs:
                need_update = check_prov(prov, municipios)
            provincias.pop(0)
            retries = 0
        except RequestException as e:
            print(str(e))
            time.sleep(config.retray_delay)
            retries += 1
    if not provincias and municipios:
        check_mun_diff(municipios)
        update(list(municipios.keys()))

def check_prov(prov_code, municipios):
    """Recoge los municipios de una provincia.

    Devuelve False si tras recoger el primero con su fecha comprueba
    que no es necesario actualizar.
    """
    for mun_code, mun_name in get_municipalities(prov_code):
        if mun_code not in config.exclude_muns:
            full_mun = mun_code[0:2] not in [m[0:2] for m in config.include_muns]
            if full_mun or mun_code in config.include_muns:
                if not municipios:
                    src_date = get_date(mun_code)
                    print("Fecha origen:", src_date)
                    if os.path.exists('src_date.txt'):
                        with open('src_date.txt', 'r') as fo:
                            last_src_date = fo.read()
                        if src_date == last_src_date:
                            return False
                municipios[mun_code] = mun_name
    return True

def check_mun_diff(municipios):
    "Compara la lista de municipios con de la anterior actualización."
    if os.path.exists('municipios.json'):
        with open('municipios.json', 'r') as fo:
            mun_prev = json.load(fo)
        #TODO: enviar por correo electrónico
        for mun_code, mun_name in municipios.items():
            if mun_code not in mun_prev:
                print(f"{mun_code} {mun_name} es nuevo")
            elif mun_prev[mun_code] != mun_name:
                print(f"{mun_code} {mun_prev[mun_code]} ha cambiado de nombre a {mun_name}")
        for mun_code, mun_name in mun_prev.items():
            if mun_code not in municipios:
                print(f"{mun_code} {mun_name} ha dejado de existir")
        shutil.move('municipios.json', 'municipios.prev.json')
    with open('municipios.json', 'w') as fo:
        json.dump(municipios, fo, indent=2)

def update(municipios):
    "Aplica multiproceso a la lista de municipios."
    src_date = get_date(municipios[0])
    len_mun = len(municipios)
    start_len_mun = len_mun
    retries = 0
    qgs = QgsSingleton()
    while municipios and retries < config.max_retries:
        print(f"Procesando {len_mun} municipios")
        with Pool(config.workers) as pool:
            if retries > 0:
                print("Reintento nro", retries)
            for mun_code in pool.imap(process, municipios):
                if mun_code is not None:
                    req = requests.get(config.uploader_url + mun_code)
                    if req.status_code == requests.codes.ok:
                        if mun_code in req.text:
                            municipios.remove(mun_code)
                            #TODO: Eliminar la carpeta
            if len(municipios) == len_mun:
                retries += 1
            else:
                len_mun = len(municipios)
                retries = 0
    if (municipios):
        print(f"Actualización {src_date} pendientes {len_mun} municipios de {start_len_mun}")
    else:
        print(f"Actualización {src_date} completados {start_len_mun} municipios")
        with open('src_date.txt', 'w') as fo:
            fo.write(src_date)
    qgs.exitQgis()

def process(mun_code):
    "Procesa un municipio individual."
    if status(mun_code) is not None:
        return mun_code
    if not os.path.exists(mun_code):
        os.mkdir(mun_code)
    log = catconfig.setup_logger(log_path=mun_code)
    pname = current_process().name.replace('ForkPool', '')
    format = f"[{pname}] [%(levelname)s] %(message)s"
    catconfig.set_log_level(log, logging.INFO, format)
    catconfig.set_config({'language': get_lang(mun_code)})
    options.path = [mun_code]
    options.args = mun_code
    try:
        CatAtom2Osm.create_and_run(mun_code, options)
        CatAtom2Osm.create_and_run(mun_code, options)
    except (BadZipfile, CatException, RequestException) as e:
        msg = e.message if getattr(e, "message", "") else str(e)
        log.error(msg)
        return None
    return status(mun_code)

def get_date(mun_code):
    "Devuelve la fecha de la fuente de datos."
    reader = catatom.Reader(mun_code)
    reader.download('address')
    (md_path, __, zip_path, __) = reader.get_layer_paths('address')
    reader.get_metadata(md_path, zip_path)
    return reader.src_date

def get_lang(mun_code):
    "Asigna idioma según provincia."
    prov = mun_code[0:2]
    language = 'es_ES'
    if prov in config.ca_provs:
        language = 'ca_ES'
    if prov in config.gl_provs:
        language = 'gl_ES'
    return language

def status(mun_code):
    """
    Comprueba estado final del procesado.
    Devuelve 'mun_code' si es correcto.
    None si hay error o no está completo.
    """
    log_file = mun_code + '/catatom2osm.log'
    if (
        os.path.exists(mun_code + '/tasks')
        and os.path.exists(mun_code + '/report.txt')
        and os.path.exists(log_file)
    ):
        with open(log_file, 'r') as fo:
            log_text = fo.read()
        return None if 'ERROR' in log_text else mun_code
    return None


if __name__ == "__main__":
    schedule.run_all()
    while True:
        schedule.run_pending()
        time.sleep(60)
