import re
import requests
import gzip
from flask import current_app
from pathlib import Path
from shapely import Polygon, MultiPolygon
from shapely.geometry import shape
from geoalchemy2.shape import from_shape, to_shape

from config import Config
from diff import Diff
from models import db, Task, TMTask, TMProject
from models.utils import get_by_area

TM_API = Config.TM_API


def fetch(url):
    data = {}
    try:
        resp = requests.get(url)
        if resp.ok:
            if resp.headers.get('Content-Type') == 'application/octet-stream':
                data = resp.content
            else:
                data = resp.json()
    except requests.RequestException as e:
        print(str(e))
    return data

def getinfo(data, key):
    value = data['projectInfo'][key]
    if value: return value
    for info in data['projectInfoLocales']:
        if info[key]: return info[key]
    return ""

def check(data, es, en, key):
    value = getinfo(data, key).lower()
    return es in value or en in value

def is_cadastre(data):
    if (
        check(data, 'catastro', 'cadastre', 'name')
        or 'Cadastre' in data.get('changesetComments', '')
        or check(data, 'catastro', 'cadastre', 'perTaskInstructions')
    ):
        return True
    return get_url_mask(data) is not None

def get_url(data):
    m = re.search(r'http[^ ]+catastro[^ ]+\.osm\.gz', data['perTaskInstructions'])
    if m: return m[0]
    return ""

def get_url_mask(data):
    url = get_url(data['projectInfo'])
    if url: return url
    for info in data['projectInfoLocales']:
        url = get_url(info)
        if url: return url
    return None

def is_buildings(data):
    return check(data, 'edificios', 'buildings', 'shortDescription')

def is_addresses(data):
    return check(data, 'direcciones', 'addresses', 'shortDescription')

def get_project(id):
    log = current_app.logger
    project = TMProject.query.get(id)
    if not project: project = TMProject(id=id)
    url = TM_API + 'projects/' + str(id)
    data = fetch(url)
    if data:
        project.name = getinfo(data, 'name')
        if is_cadastre(data):
            log.info(f"Comprueba proyecto TM#{id} {project.name}")
            project.buildings = is_buildings(data)
            project.addresses = is_addresses(data)
            if not project.buildings and not project.addresses:
                project.buildings = True
                project.addresses = True
            project.created = data['created'].split('T')[0]
            pending_tasks = data['tasks']['features']
            tmtasks = get_tasks(project, pending_tasks)
            if tmtasks: link_tasks(tmtasks)
            db.session.add(project)
    return project

def get_tasks(project, pending_tasks):
    log = current_app.logger
    tmtasks = []
    task_count = 0
    for feat in pending_tasks:
        id = feat['properties']['taskId']
        tmtask = TMTask.query.get(id)
        if not tmtask: tmtask = TMTask(id=id)
        tmtask.status = feat['properties']['taskStatus']
        shp = shape(feat['geometry']).buffer(0)
        if isinstance(shp, Polygon): shp = MultiPolygon([shp])
        tmtask.geom = from_shape(shp)
        data = fetch(f"{TM_API}projects/{project.id}/tasks/{id}")
        if data:
            url = get_url(data)
            tmtask.muncode, tmtask.filename = url.split('/')[-2:]
            path = Path(tmtask.get_path())
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                resp = requests.get(url)
                if resp.ok:
                    data = fetch(url)
                    if data:
                        if b'<node ' not in gzip.decompress(data):
                            log.info(f"Tarea TM#{project.id}-{id} {tmtask.filename} vacía")
                            task_count += 1
                        else:
                            with path.open('wb') as fo:
                                fo.write(data)
                            tmtask.project = project
                            tmtasks.append(tmtask)
                            db.session.add(tmtask)
                            task_count += 1
                            log.info(f"Descarga tarea TM#{project.id}-{id} {tmtask.filename} {tmtask.status}")
                if resp.status_code == 404:
                    task_count += 1
                    log.info(f"Tarea TM#{project.id}-{id} {tmtask.filename} no encontrada")
    if task_count != len(pending_tasks):
        log.info(f"TM#{project.id} Faltan {len(pending_tasks) - task_count} tareas por descargar")
        return []
    return tmtasks

def link_tasks(tmtasks):
    for tmtask in tmtasks:
        tasks = get_by_area(Task, tmtask.geom)
        print(tmtask.id, len(tasks))

def get_projects():
    url = TM_API + 'projects/?action=any'
    data = fetch(url)
    if data:
        for feat in data['mapResults']['features']:
            id = feat['properties']['projectId']
            project = get_project(id)
    # projectStatuses=ARCHIVED