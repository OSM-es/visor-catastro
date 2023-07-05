from datetime import datetime
from enum import Enum

from geoalchemy2 import Geometry, Index

from models import db, TaskHistory, TaskLock


class Task(db.Model):
    class Status(Enum):
        READY = 0
        MAPPED = 2
        VALIDATED = 4
        INVALIDATED = 5
        NEED_UPDATE = 6

        @staticmethod
        def from_action(action):
            return Task.Status(action)

    class Difficulty(Enum):
        EASY = 1
        MODERATE = 2
        CHALLENGING = 3

    id = db.Column(db.Integer, primary_key=True)
    muncode = db.Column(db.String, index=True)
    localId = db.Column('localid', db.String, index=True)
    zone = db.Column(db.String)
    type = db.Column(db.String)
    ad_status = db.Column(db.Integer, default=Status.READY.value)
    bu_status = db.Column(db.Integer, default=Status.READY.value)
    parts = db.Column(db.Integer)
    buildings = db.Column(db.Integer)
    addresses = db.Column(db.Integer)
    difficulty = db.Column(db.Integer)
    lock_id = db.Column(db.Integer, db.ForeignKey('task_lock.id'), nullable=True)
    lock = db.relationship('TaskLock', viewonly=True)
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
            'ad_mapper': self.ad_mapper.asdict() if self.ad_mapper else None,
            'bu_mapper': self.bu_mapper.asdict() if self.bu_mapper else None,
            'history': [h.asdict() for h in self.history]
        }

    def update_lock(self):
        if self.lock:
            age = (datetime.now() - self.lock.date).total_seconds()
            if age > self.lock.timeout:
                # Añadir AUTO_UNLOCKED a historial
                db.session.delete(self.lock)
                db.session.commit()
    
    def set_lock(self, user, action, buildings, addresses):
        if self.lock or user.user.lock:
            raise PermissionError
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
        self.history.append(h)
        db.session.add(lock)
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
            raise ValueError
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
        raise ValueError

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
