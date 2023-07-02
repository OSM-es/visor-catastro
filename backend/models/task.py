from datetime import datetime
from enum import Enum

from geoalchemy2 import Geometry, Index

from models import db, TaskHistory

TASK_LOCK_TIMEOUT = 86400


class Task(db.Model):
    class Status(Enum):
        READY = 0
        LOCKED_FOR_MAPPING = 1
        MAPPED = 2
        LOCKED_FOR_VALIDATION = 3
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
    history = db.relationship('TaskHistory', back_populates='task')
    geom = db.Column(Geometry("GEOMETRYCOLLECTION", srid=4326))
    __table_args__ = (Index('codes_index', 'localid', 'muncode'), )

    @staticmethod
    def get_by_code(mun_code, local_id):
        return Task.query.filter(Task.muncode == mun_code, Task.localId == local_id).one_or_none()

    def __str__(self):
        return f"{self.muncode} {self.localId} {self.type} {self.parts}"

    def asdict(self):
        owner = self.owner
        ad_mapper = self.ad_mapper
        bu_mapper = self.bu_mapper
        ad_validator = self.ad_validator
        bu_validator = self.bu_validator
        return {
            'id': self.id,
            'localId': self.localId,
            'muncode': self.muncode,
            'type': self.type,
            'difficulty': Task.Difficulty(self.difficulty).name,
            'ad_status': Task.Status(self.ad_status).name,
            'bu_status': Task.Status(self.bu_status).name,
            'is_locked': self.is_locked(),
            'owner': owner.asdict() if owner else None,
            'ad_mapper': ad_mapper.asdict() if ad_mapper else None,
            'bu_mapper': bu_mapper.asdict() if bu_mapper else None,
            'ad_validator': ad_validator.asdict() if ad_validator else None,
            'bu_validator': bu_validator.asdict() if bu_validator else None,
        }

    def is_locked(self):
        if self.history:
            last = self.history[-1]
            if last.action in TaskHistory.lock_actions:
                age = (datetime.now() - last.date).total_seconds()
                if age < TASK_LOCK_TIMEOUT:
                    return Task.Status.from_action(last.action).name
        return None

    def last_action(self, target, *actions):
        i = len(self.history) - 1
        while (
            i >= 0
            and self.history[i].action not in actions
            and not getattr(self.history[i], target)
        ):
            i -= 1
        if (i >= 0):
            return self.history[i]
        return None

    @property
    def owner(self):
        if self.is_locked():
            return self.history[-1].user
        return None

    @property
    def ad_mapper(self):
        mapper = self.last_action('addresses', TaskHistory.Action.MAPPED)
        return mapper and mapper.user

    @property
    def bu_mapper(self):
        mapper = self.last_action('buildings', TaskHistory.Action.MAPPED)
        return mapper and mapper.user

    @property
    def ad_validator(self):
        val = self.last_action(
            'addresses',
            TaskHistory.Action.VALIDATED,
            TaskHistory.Action.INVALIDATED,
        )
        return val and val.user

    @property
    def bu_validator(self):
        val = self.last_action(
            'buildings',
            TaskHistory.Action.VALIDATED,
            TaskHistory.Action.INVALIDATED,
        )
        return val and val.user

    def add_history(self, user, target):
        action = TaskHistory.Action.VALIDATED.value if self.validated else TaskHistory.Action.RESET.value
        self.history.append(TaskHistory(user=user, action=action, target=target))
