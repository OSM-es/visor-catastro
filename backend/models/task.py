from datetime import datetime
from enum import Enum
from pytz import UTC

from geoalchemy2 import Geometry, Index
from geoalchemy2.shape import from_shape
from sqlalchemy import and_, func

from models import db, History, Municipality, TaskHistory, TaskLock, OsmUser
from models.utils import get_by_area


class Task(db.Model):
    """
    Es la unidad mínima de trabajo de la importación. Está representada por la
    geometría de un área delimitadora. Tiene asociado un archivo conteniendo las
    direcciones y edificios a importar.

    Se corresponde con una parcela catastral pero no existe una relación uno a
    uno. El programa de conversión, para intentar mantener una dificultad 
    uniforme, agrupa en una tarea algunas parcelas adyacentes pequeñas,
    mientras que intenta dividir las parcelas más grandes.
    La limitación es que los edificios con paredes colindantes se mantienen en
    la misma tarea.
    """
    class Status(Enum):
        READY = 0  # Disponible para importar.
        MAPPED = 2  # El usuario terminó de importar.
        VALIDATED = 4  # Un usuario (diferente al mapeador) da la tarea por buena.
        INVALIDATED = 5  # Un usuario (diferente al mapeador) cree que hace falta mapeo adicional.
        NEED_UPDATE = 6  # Se ha producido una actualización de Catastro, hay cambios que es necesario mapear.

    class Difficulty(Enum):
        """Se calcula a partir del máximo de parts (valor original), buildings y addresses"""
        EASY = 1  # 0-9
        MODERATE = 2  # 10-19
        CHALLENGING = 3  # >= 20

        @staticmethod
        def get_from_complexity(buildings, parts, addresses):
            complexity = max(buildings, parts, addresses)
            difficulty = Task.Difficulty['EASY']
            if complexity >= Task.CHALLENGING_THRESHOLD:
                difficulty = Task.Difficulty['CHALLENGING']
            elif complexity >= Task.MODERATE_THRESHOLD:
                difficulty = Task.Difficulty['MODERATE']
            return difficulty

    class Update(db.Model):
        """
        Almacén temporal de nuevas tareas para actualizar.
        """
        __tablename__ = 'task_update'

        id = db.Column(db.Integer, primary_key=True)
        muncode = db.Column(db.String, nullable=True)
        localId = db.Column('localid', db.String)
        zone = db.Column(db.String)
        type = db.Column(db.String)
        task = db.relationship('Task', back_populates='update', uselist=False)
        geom = db.Column(Geometry("GEOMETRYCOLLECTION", srid=4326))

        @staticmethod
        def from_feature(feature):
            u = Task.Update(**feature['properties'])
            if u.type == 'R&uacute;stica': u.type = 'Rústica'
            geom = feature['geometry']
            u.geom = from_shape(geom)
            return u

        @staticmethod
        def get_path(mun_code, filename):
            return Municipality.Update.get_path(mun_code) + '/tasks/' + filename

        def path(self):
            return Task.Update.get_path(self.muncode, self.localId + '.osm.gz')

    MODERATE_THRESHOLD = 10
    CHALLENGING_THRESHOLD = 20
    BUFFER = 0.00005  # Márgen de desplazamiento por correcciones de precisión

    id = db.Column(db.Integer, primary_key=True)
    # Código de Catastro del municipio. Coincide en ocasiones con el código postal o código INE, pero no siempre.
    muncode = db.Column(db.String, index=True, nullable=False)
    # Identificador asignado por el programa conversor a partir de la referencia catastral de la parcela.
    # Puede repetirse en otro municipio.
    # No es inmutable por que las parcelas pueden segregarse o agregarse.
    localId = db.Column('localid', db.String, index=True)
    zone = db.Column(db.String)  # relic
    type = db.Column(db.String)  # Urbana / Rústica
    # Ver Status. Si coinciden, se están importando conjuntamente, si no,
    # se ha elegido importar cada subconjunto de datos por separado.
    ad_status = db.Column(db.Integer, default=Status.READY.value)
    bu_status = db.Column(db.Integer, default=Status.READY.value)
    # Número de partes de edificio (secciones diferenciadas por número de alturas). 
    # En origen existe al menos una parte para cada edificio, en los archivos 
    # de tareas convertidos, si sólo existe una parte desaparece y su altura se
    # pasa al edificio.
    parts = db.Column(db.Integer)
    # Número de edificios
    buildings = db.Column(db.Integer)
    # Número de direcciones. Algunas están en un nodo (entrada), otras en un edificio.
    addresses = db.Column(db.Integer)
    # Número de piscinas
    pools = db.Column(db.Integer)
    difficulty = db.Column(db.Integer)  # Ver Difficulty
    # Es usado por la consulta get del recurso tasks para saber el estado sin hacer join
    lock_id = db.Column(db.Integer, db.ForeignKey('task_lock.id'), nullable=True)
    # Bloqueo para mapear o validar. Tendrán un tiempo de caducidad.
    lock = db.relationship('TaskLock', viewonly=True)
    # Registro de los cambios realizados en la tarea más comentarios.
    history = db.relationship('TaskHistory', back_populates='task')
    # Anotaciones para correcciones por el editor
    fixmes = db.relationship('Fixme', back_populates='task')
    update_id = db.Column(db.Integer, db.ForeignKey('task_update.id'), nullable=True)
    update = db.relationship(Update, back_populates='task', uselist=False)
    geom = db.Column(Geometry("GEOMETRYCOLLECTION", srid=4326))
    __table_args__ = (Index('codes_index', 'localid', 'muncode'), )

    @staticmethod
    def get_by_ref(mun_code, local_id):
        return Task.query.filter(Task.muncode == mun_code, Task.localId == local_id).one_or_none()

    @staticmethod
    def query_by_code(code):
        if code and len(code) == 5:
            return Task.query.filter(Task.muncode == code)
        elif code and len(code) == 2:
            return Task.query.filter(Task.muncode.startswith(code))
        return Task.query

    @staticmethod
    def query_by_muncode(mun_code):
        return Task.query.filter(Task.muncode == mun_code)

    @staticmethod
    def query_by_provcode(prov_code):
        return Task.query.filter(Task.muncode.startswith(prov_code))

    @staticmethod
    def query_mapped(query):
        mapped = [Task.Status.MAPPED.value, Task.Status.VALIDATED.value]
        return query.filter(and_(Task.ad_status.in_(mapped), Task.bu_status.in_(mapped)))

    @staticmethod
    def from_feature(feature):
        del feature['properties']['parts']
        task = Task(**feature['properties'])
        if task.type == 'R&uacute;stica': task.type = 'Rústica'
        shape = feature['geometry']
        task.geom = from_shape(shape)
        return task

    @staticmethod
    def status_stats(mun_code, attr):
        statuses = [s.value for s in Task.Status]
        stats = [0] * len(Task.Status)
        f = getattr(Task, attr)
        q = Task.query_by_muncode(mun_code).with_entities(
            f, func.count(f)
        ).group_by(f)
        for k, v in q.all():
            stats[statuses.index(k)] = v
        return stats

    @staticmethod
    def count_locks(code, type, attr):
        f = getattr(TaskLock, attr)
        t = TaskLock.Action(type).name
        c = Task.query_by_code(code).join(TaskLock).filter(
            and_(TaskLock.text == t, f)
        ).count()
        return c

    @staticmethod
    def get_match(feature):
        new_task = Task.from_feature(feature)
        candidates = get_by_area(Task, new_task.geom, buffer=Task.BUFFER)
        if candidates:
            for c in candidates:
                c.update = Task.Update()
            u = Task.Update.from_feature(feature)
            old_task = next(
                (c for c in candidates if c.localId == u.localId and c.update_id is None),
                candidates[0]
            )
            task = old_task
            task.update = u
        else:
            db.session.add(new_task)
            task = new_task
        return task, candidates

    @staticmethod
    def get_by_shape(shape):
        geom = from_shape(shape)
        return get_by_area(Task, geom)

    @staticmethod
    def update_tasks(mun_code):
        for u in Task.Update.query.filter(Task.Update.muncode == mun_code):
            if not u.muncode:
                u.task.update = None
                continue
            u.task.muncode = u.muncode
            u.task.localId = u.localId
            u.task.zone = u.zone
            u.task.type = u.type
            u.task.geom = u.geom
            u.task.set_need_update()
            u.task.update = None
        Task.Update.query.filter(Task.Update.muncode == mun_code).delete()

    @staticmethod
    def get_path(mun_code, filename):
        return Municipality.get_path(mun_code) + '/tasks/' + filename

    @staticmethod
    def count_buildings(muncode=None):
        q = Task.query.with_entities(
            func.sum(Task.buildings)
        ).filter(
            Task.bu_status != 0
        )
        if muncode: q = q.filter_by(muncode = muncode)
        return q.scalar() or 0

    @staticmethod
    def count_addresses(muncode=None):
        q = Task.query.with_entities(
            func.sum(Task.addresses)
        ).filter(
            Task.ad_status != 0
        )
        if muncode: q = q.filter_by(muncode = muncode)
        return q.scalar() or 0

    @staticmethod
    def count_mappers(muncode=None):
        q = Task.query.join(
            TaskLock
        ).with_entities(
            func.count(TaskLock.user_id.distinct())
        )
        if muncode: q = q.filter(Task.muncode == muncode)
        return q.scalar() or 0

    def path(self):
        return Task.get_path(self.muncode, self.localId + '.osm.gz')

    def __str__(self):
        return f"{self.muncode} {self.localId} {self.type}"

    def asdict(self):
        if self.lock:
            self.lock.update_lock()
            db.session.commit()
        lock = self.lock.asdict() if self.lock else None
        return {
            'id': self.id,
            'localId': self.localId,
            'muncode': self.muncode,
            'type': self.type,
            'difficulty': Task.Difficulty(self.difficulty).name,
            'ad_status': Task.Status(self.ad_status).name,
            'bu_status': Task.Status(self.bu_status).name,
            'lock': lock,
            'ad_mapper': self.ad_mapper.user.asdict() if self.ad_mapper else None,
            'bu_mapper': self.bu_mapper.user.asdict() if self.bu_mapper else None,
            'history': [h.asdict() for h in self.history]
        }

    def set_lock(self, user, action, buildings, addresses):
        if self.lock or user.user.lock:
            raise PermissionError
        if not buildings and not addresses:
            raise ValueError("Se debe especificar al menos edificios o direcciones")
        if action == TaskHistory.Action.UNLOCKED:
            return self.unlock()
        h = TaskHistory(
            user=user,
            action=action.value,
            text='',
            buildings=buildings,
            addresses=addresses,
        )
        lock = TaskLock(
            action=action.value,
            user=user.user,
            task=self,
            text=action.name,
            buildings=buildings,
            addresses=addresses,
            history=h,
        )
        db.session.add(lock)
        self.history.append(h)
    
    def unlock(self, user):
        if not self.lock or self.lock.user != user.user:
            raise PermissionError
        self.lock.history.text = self.lock.time_elapsed
        h = TaskHistory(
            user=user,
            action=TaskHistory.Action.UNLOCKED.value,
            text=self.lock.text,
            buildings=self.lock.buildings,
            addresses=self.lock.addresses,
        )
        self.history.append(h)
        db.session.delete(self.lock)

    def need_update(self):
        return any([f.is_update() for f in self.fixmes])

    def set_need_update(self):
        if not self.need_update():
            return
        user=OsmUser.system_bot()
        addresses = self.ad_status != Task.Status.READY.value
        buildings = self.bu_status != Task.Status.READY.value
        if buildings or addresses:
            self.change_status(
                user, Task.Status.NEED_UPDATE, buildings, addresses, check_lock=False
            )

    def change_status(self, user, status, buildings, addresses, check_lock=True):
        if check_lock and (not self.lock or self.lock.user != user.user):
            raise PermissionError
        if not buildings and not addresses:
            raise ValueError("Se debe especificar al menos edificios o direcciones")
        if addresses:
            self.validate_status('ad_status', status)
        if buildings:
            self.validate_status('bu_status', status)
        h = TaskHistory(
            user=user,
            action=TaskHistory.Action.STATE_CHANGE.value,
            text=status.name,
            buildings=buildings,
            addresses=addresses,
        )
        self.history.append(h)
        if self.lock: db.session.delete(self.lock)
    
    def validate_status(self, key, status):
        old = Task.Status(getattr(self, key))
        if (
            status == Task.Status.NEED_UPDATE and old != Task.Status.READY
            or status == Task.Status.MAPPED and old in (
                Task.Status.READY,
                Task.Status.INVALIDATED,
                Task.Status.NEED_UPDATE,
            )
            or old == Task.Status.MAPPED and status in (
                Task.Status.VALIDATED,
                Task.Status.INVALIDATED,
            )
        ):
            setattr(self, key, status.value)
            return
        raise ValueError(f"Valores erróneos {old} => {status}")

    def last_action(self, target, action, text):
        i = len(self.history) - 1
        while (
            i >= 0 and (
                self.history[i].action != action
                or self.history[i].text != text
                or not getattr(self.history[i], target)
            )
        ):
            i -= 1
        if (i >= 0):
            return self.history[i]
        return None

    def both_ready(self):
        return (
            self.ad_status == Task.Status.READY.value
            and self.bu_status == Task.Status.READY.value
        )

    def delete(self):
        for h in self.history:
            db.session.delete(h)
        db.session.delete(self)
        h = History(action=History.Action.DEL_TASK.value)
        db.session.add(h)

    @property
    def ad_mapper(self):
        mapper = self.last_action(
            'addresses',
            TaskHistory.Action.STATE_CHANGE.value,
            Task.Status.MAPPED.name,
        )
        return mapper and mapper.user

    @property
    def bu_mapper(self):
        mapper = self.last_action(
            'buildings',
            TaskHistory.Action.STATE_CHANGE.value,
            Task.Status.MAPPED.name,
        )
        return mapper and mapper.user
