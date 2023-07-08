from datetime import datetime
from enum import Enum
from pytz import UTC

from geoalchemy2 import Geometry, Index

from models import db, TaskHistory, TaskLock


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

    MODERATE_THRESHOLD = 10
    CHALLENGING_THRESHOLD = 20

    id = db.Column(db.Integer, primary_key=True)
    # Código de Catastro del municipio. Coincide en ocasiones con el código postal o código INE, pero no siempre.
    muncode = db.Column(db.String, index=True)
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
    difficulty = db.Column(db.Integer)  # Ver Difficulty
    # Es usado por la consulta get del recurso tasks para saber el estado sin hacer join
    lock_id = db.Column(db.Integer, db.ForeignKey('task_lock.id'), nullable=True)
    # Bloqueo para mapear o validar. Tendrán un tiempo de caducidad.
    lock = db.relationship('TaskLock', viewonly=True)
    # Registro de los cambios realizados en la tarea más comentarios.
    history = db.relationship('TaskHistory', back_populates='task')
    geom = db.Column(Geometry("GEOMETRYCOLLECTION", srid=4326))
    __table_args__ = (Index('codes_index', 'localid', 'muncode'), )

    @staticmethod
    def get_by_code(mun_code, local_id):
        return Task.query.filter(Task.muncode == mun_code, Task.localId == local_id).one_or_none()

    def __str__(self):
        return f"{self.muncode} {self.localId} {self.type} {self.parts}"

    def asdict(self):
        self.update_lock()
        return {
            'id': self.id,
            'localId': self.localId,
            'muncode': self.muncode,
            'type': self.type,
            'difficulty': Task.Difficulty(self.difficulty).name,
            'ad_status': Task.Status(self.ad_status).name,
            'bu_status': Task.Status(self.bu_status).name,
            'lock': self.lock.asdict() if self.lock else None,
            'ad_mapper': self.ad_mapper.user.asdict() if self.ad_mapper else None,
            'bu_mapper': self.bu_mapper.user.asdict() if self.bu_mapper else None,
            'history': [h.asdict() for h in self.history]
        }

    def update_lock(self):
        if self.lock:
            age = (datetime.now(tz=UTC) - self.lock.date).total_seconds()
            if age > self.lock.timeout:
                # Añadir AUTO_UNLOCKED a historial
                db.session.delete(self.lock)
                db.session.commit()
    
    def set_lock(self, user, action, buildings, addresses):
        if self.lock or user.user.lock:
            raise PermissionError
        if not buildings and not addresses:
            raise ValueError("Se debe especificar al menos edificios o direcciones")
        if action == TaskLock.Action.UNLOCK:
            return self.unlock()
        lock = TaskLock(
            user=user.user,
            task=self,
            text=action.name,
            buildings=buildings,
            addresses=addresses
        )
        h = TaskHistory(
            user=user,
            action=TaskHistory.Action.LOCKED.value,
            text=action.name,
            buildings=buildings,
            addresses=addresses,
        )
        db.session.add(lock)
        self.history.append(h)
        db.session.commit()
    
    def unlock(self, user):
        if not self.lock or self.lock.user != user.user:
            raise PermissionError
        h = TaskHistory(
            user=user,
            action=TaskHistory.Action.UNLOCKED.value,
            text=self.lock.text,
            buildings=self.lock.buildings,
            addresses=self.lock.addresses,
        )
        self.history.append(h)
        db.session.delete(self.lock)
        db.session.commit()

    def change_status(self, user, status, buildings, addresses):
        if not self.lock or self.lock.user != user.user:
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
        db.session.delete(self.lock)
        db.session.commit()
    
    def validate_status(self, key, status):
        old = Task.Status(getattr(self, key))
        if status == Task.Status.MAPPED and old in (
            Task.Status.READY,
            Task.Status.INVALIDATED,
            Task.Status.NEED_UPDATE,
        ):
            setattr(self, key, status.value)
            return
        elif old == Task.Status.MAPPED and status in (
            Task.Status.VALIDATED,
            Task.Status.INVALIDATED,
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
