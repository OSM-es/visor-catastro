import re
import requests
import gzip
from flask import current_app
from pathlib import Path
from shapely import Polygon, MultiPolygon
from shapely.geometry import shape
from geoalchemy2.shape import from_shape, to_shape

from auth import passTutorial
from config import Config
from diff import Diff
from models import db, Task, TaskHistory, TMTask, TMProject, OsmUser, User
from models.utils import get_by_area

TM_API = Config.TM_API
OSM_API = Config.OSM_API
OSM_URL = Config.OSM_URL


def fetch(url):
    data = {}
    try:
        resp = requests.get(url)
        if resp.ok:
            if resp.headers.get('Content-Type') == 'application/octet-stream':
                data = resp.content
            elif resp.headers.get('Content-Type') == 'text/html; charset=utf-8':
                data = resp.text
            elif resp.headers.get('Content-Type') == 'application/xml; charset=utf-8':
                data = resp.text
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
            db.session.add(project)
            db.session.commit()
            get_project_users(project)
            if project.status == TMProject.Status.DOWNLOADING.value:
                tmtasks = get_tasks(project, data['tasks']['features'])
                if tmtasks:
                    project.status = TMProject.Status.DOWNLOADED.value
                    db.session.commit()
                link_tasks(tmtasks)
            else:
                tmtasks = list(TMTask.query.filter_by(project_id = project.id).all())
            update_tasks_statuses(project)
            update_tasks_history(project, tmtasks)
    return project

def get_project_users(project):
    log = current_app.logger
    url = f'{TM_API}projects/{project.id}/contributions'
    data = fetch(url)
    users_count = 0
    new_users = 0
    if data:
        contributions = data['userContributions']
        for tmuser in contributions:
            username = tmuser['username']
            id = get_user_id(username)
            if id:
                osm_user = OsmUser.query.get(id)
                if not osm_user:
                    osm_user = OsmUser(id=id, display_name=username, img=tmuser['pictureUrl'])
                    db.session.add(osm_user)
                    new_users += 1
                    if osm_user.isStated():
                        user = User(
                            mapping_level=User.MappingLevel[tmuser['mappingLevel']].value,
                            date_registered=tmuser['dateRegistered'],
                        )
                        user.import_user = osm_user
                        passTutorial(user)
                        db.session.add(user)
                    db.session.commit()
                users_count +=1
        if users_count == len(contributions):
            if new_users:
                log.info(f"TM#{project.id} Migrados {users_count} usuarios")
        else:
            log.info(f"TM#{project.id} Falta comprobar {len(contributions) - users_count} usuarios")
            return -1
    return users_count


def get_user_id(username):
    cid = get_changeset_id(username)
    if cid:
        url = f'{OSM_API}changeset/{cid}'
        data = fetch(url)
        if data:
            m = re.search(r' uid="(\d+)"', data)
        if m:
            return m.group(1)
    return None

def get_changeset_id(username):
    url = f'{OSM_URL}/user/{username}/history?list=1'
    data = fetch(url)
    if data:
        m = re.search(r'changeset/(\d+)', data)
        if m:
            return m.group(1)
    return None

def get_tasks(project, pending_tasks):
    log = current_app.logger
    tmtasks = []
    task_count = 0
    for feat in pending_tasks:
        id = feat['properties']['taskId']
        tmtask = TMTask.query.get(id)
        if not tmtask: tmtask = TMTask(id=id)
        tmtask.project = project
        tmtask.status = feat['properties']['taskStatus']
        shp = shape(feat['geometry']).buffer(0)
        if isinstance(shp, Polygon): shp = MultiPolygon([shp])
        tmtask.geom = from_shape(shp)
        data = fetch(f"{TM_API}projects/{project.id}/tasks/{id}")
        if data:
            url = get_url(data)
            tmtask.muncode, tmtask.filename = url.split('/')[-2:]
            path = Path(tmtask.get_path())
            if path.exists():
                tmtasks.append(tmtask)
                db.session.add(tmtask)
                task_count += 1
            else:
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
                            tmtasks.append(tmtask)
                            db.session.add(tmtask)
                            task_count += 1
                            log.info(f"Descarga tarea TM#{project.id}-{id} {tmtask.filename}")
                if resp.status_code == 404:
                    task_count += 1
                    log.info(f"Tarea TM#{project.id}-{id} {tmtask.filename} no encontrada")
    if task_count != len(pending_tasks):
        log.info(f"TM#{project.id} Faltan {len(pending_tasks) - task_count} tareas por descargar")
        return []
    return tmtasks

def link_tasks(tmtasks):
    for tmtask in tmtasks:
        for task in get_by_area(Task, tmtask.geom, percentaje=0.01):
            task.tmtasks.append(tmtask)
    
def update_tasks_statuses(project):
    tasks = Task.query.join(Task.tmtasks).filter_by(project_id=207).distinct()
    for task in tasks.all():
        statuset = {t.status for t in task.tmtasks if not t.status.startswith('LOCKED_FOR_')}
        if not statuset:
            continue
        status = list(statuset)[0]
        if len(statuset) > 1:
            if Task.Status.READY.name in statuset or Task.Status.INVALIDATED.name in statuset:
                status = Task.Status.INVALIDATED.name
            else:
                status = Task.Status.MAPPED.name
        status = Task.Status[status].value
        if project.buildings:
            task.bu_status = status
        if project.addresses:
            task.ad_status = status
    db.session.commit()

def update_tasks_history(project, tmtasks):
    for tmtask in tmtasks:
        data = fetch(f"{TM_API}projects/{project.id}/tasks/{tmtask.id}")
        taskHistory = data['taskHistory'] if data else []
        for history in taskHistory:
            user = OsmUser.query.filter_by(display_name = history['actionBy']).one_or_none()
            if not user:
                continue
            date = history['actionDate']
            action = history['action']
            text = history['actionText']
            if 'LOCKED_FOR_' in action:
                if text:
                    text = str(int(sum(x * float(t) for x, t in zip([3600, 60, 1], text.split(":")))))
                if action.startswith('AUTO_UNLOCKED_FOR_'):
                    action = action[7:]
            elif action.startswith('EXTENDED_FOR_'):
                action = 'EXTENDED'
            for task in tmtask.tasks:
                if TaskHistory.query.filter_by(
                    date = date, user = user, task = task
                ).count() == 0:
                    h = TaskHistory(
                        date=date,
                        user=user,
                        action=TaskHistory.Action[action].value,
                        text=text,
                        buildings=project.buildings,
                        addresses=project.addresses,
                    )
                    task.history.append(h)
    db.session.commit()

def get_projects():
    url = TM_API + 'projects/?action=any'
    data = fetch(url)
    if data:
        for feat in data['mapResults']['features']:
            id = feat['properties']['projectId']
            get_project(id)
    # projectStatuses=ARCHIVED