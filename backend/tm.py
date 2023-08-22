import re
import requests
from collections import defaultdict
from pathlib import Path
from shapely.geometry import shape
from geoalchemy2.shape import from_shape

from diff import Diff
from models import Municipality, Task
from models.utils import get_by_area

BASE = 'https://tareas.openstreetmap.es/api/v2/'


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
    url = BASE + 'projects/' + str(id)
    data = fetch(url)
    project = {}
    if data:
        project['id'] = str(id)
        project['name'] = getinfo(data, 'name')
        project['cadastre'] = is_cadastre(data)
        if project['cadastre']:
            project['status'] = 'PUBLISHED'
            project['buildings'] = is_buildings(data)
            project['addrseses'] = is_addresses(data)
            if not project['buildings'] and not project['addrseses']:
                project['buildings'] = True
                project['addrseses'] = True
            project['created'] = data['created'].split('T')[0]
            project['pending_tasks'] = data['tasks']['features']
    return project

def get_tasks(project):
    tmtasks = {}
    for feat in project['pending_tasks']:
        id = feat['properties']['taskId']
        status = feat['properties']['taskStatus']
        shp = shape(feat['geometry']).buffer(0)
        data = fetch(f"{BASE}projects/{project['id']}/tasks/{id}")
        if data:
            url = get_url(data)
            muncode, filename = url.split('/')[-2:]
            path = Path(Task.Update.get_path(muncode, filename))
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                resp = requests.get(url)
                if resp.ok:
                    file = fetch(url)
                    if file:
                        with path.open('wb') as fo:
                            fo.write(file)
                elif resp.status_code != 404:
                    continue
                tmtasks[id] = {
                    'status': status,
                    'muncode': muncode,
                    'filename': filename,
                    'shape': shp,
                }
                print(id, status, muncode, filename, resp.status_code)
    #     continue
    #     if status == Task.Status.READY.name:
    #         # candidates = get_by_area(Municipality, geom, percentaje=0.6, buffer=Task.BUFFER)
    #         candidates = get_by_area(Task, geom, percentaje=0.9, buffer=Task.BUFFER)
    #         for c in candidates:
    #             tasks[c.id].append(tid)
    #             tmtasks[tid] = status
    #             print(tid, status, len(candidates))
    #     print()
    # for k, v in tasks.items():
    #     print(k, v, [tmtasks[t] for t in v])
    if len(tmtasks) == len(project['pending_tasks']):
        del project['pending_tasks']

def get_projects():
    url = BASE + 'projects/?action=any'
    data = fetch(url)
    if data:
        for feat in data['mapResults']['features']:
            id = feat['properties']['projectId']
            # busca en bd, si no lo encuentra lo crea con resultado de get_project
            project = get_project(id)
            if project['cadastre']:
                get_tasks(project)
            if 'pending_tasks' in project:
                print('pendiente', project['name'])
            else:
                print(project)
    # projectStatuses=ARCHIVED