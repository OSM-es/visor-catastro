from datetime import datetime
from enum import Enum
from pytz import UTC

from sqlalchemy import column, func, or_, and_
from sqlalchemy.orm import declarative_mixin

from models import db, OsmUser, User
import models

TASK_LOCK_TIMEOUT = 7200


class HistoryMixin:
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(
        db.DateTime(timezone=True),
        server_default=db.func.now(), 
        index=True,
    )


@declarative_mixin
class TaskHistoryMixin:
    __table_args__ = (
        db.CheckConstraint(or_(column('buildings'), column('addresses')), name='ck_bd_or_ad'),
    )

    text = db.Column(db.String)
    buildings = db.Column(db.Boolean, nullable=False)
    addresses = db.Column(db.Boolean, nullable=False)


class History(HistoryMixin, db.Model):
    class Action(Enum):
        DEL_TASK = 1
        DEL_MUNICIPALITY = 2
        DEL_STREET = 3

    type = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('osm_user.id'), nullable=False)
    user = db.relationship('OsmUser', back_populates='history')
    action = db.Column(db.Integer, nullable=False)

    __mapper_args__ = {'polymorphic_on': 'type', 'polymorphic_identity': 'H'}

    def __init__(self, *args, **kwargs):
        if 'user' not in kwargs:
            kwargs['user'] = OsmUser.system_bot()
        super(History, self).__init__(*args, **kwargs)

    @property
    def target(self):
        return self.task if isinstance(self, TaskHistory) else self.street


class TaskHistory(TaskHistoryMixin, History):
    class Action(Enum):
        LOCKED_FOR_MAPPING = 1
        LOCKED_FOR_VALIDATION = 2
        STATE_CHANGE = 3
        COMMENT = 4
        UNLOCKED = 5
        AUTO_UNLOCKED = 6
        EXTENDED = 7

        @staticmethod
        def from_status(status):
            return TaskHistory.Action(status)

    id = db.Column(db.Integer, db.ForeignKey('history.id'), primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    task = db.relationship('Task', back_populates='history')

    __mapper_args__ = {'polymorphic_identity': 'TH'}

    def asdict(self):
        return {
            'date': self.date.isoformat(),
            'user': self.user.display_name,
            'avatar': self.user.img,
            'action': TaskHistory.Action(self.action).name,
            'text': self.text,
            'addresses': self.addresses,
            'buildings': self.buildings,
        }

    @staticmethod
    def _count_contributors(muncode, _target='MAPPED'):
        return TaskHistory.query.join(
            OsmUser
        ).join(
            User, or_(User.osm_id == OsmUser.id, User.import_id == OsmUser.id)
        ).join(
            models.Task
        ).filter_by(
            muncode = muncode
        ).filter(
            and_(TaskHistory.action == 2, TaskHistory.text == _target)
        ).distinct(
            User.id
        ).count()

    @staticmethod
    def count_mappers(muncode):
        return TaskHistory._count_contributors(muncode, 'MAPPED')

    @staticmethod
    def count_validators(muncode):
        return TaskHistory._count_contributors(muncode, 'VALIDATED')

    @staticmethod
    def get_contributors(muncode):
        return TaskHistory.query.join(
            OsmUser
        ).join(
            User, or_(User.osm_id == OsmUser.id, User.import_id == OsmUser.id)
        ).join(
            models.Task
        ).filter_by(
            muncode = muncode
        ).filter(
            TaskHistory.action == 2
        ).with_entities(
            User
        ).distinct().all()


class TaskLock(HistoryMixin, TaskHistoryMixin, db.Model):
    class Action(Enum):
        MAPPING = 1
        VALIDATION = 2

    timeout = db.Column(db.Integer, nullable=False, default=TASK_LOCK_TIMEOUT)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)
    user = db.relationship('User', back_populates='lock')
    task = db.relationship('Task', back_populates='lock', uselist=False)
    history_id = db.Column(db.Integer, db.ForeignKey('task_history.id', use_alter=True))
    history = db.relationship('TaskHistory')

    def asdict(self):
        return {
            'date': self.date.isoformat(),
            'user': self.user.asdict(),
            'text': self.text,
            'addresses': self.addresses,
            'buildings': self.buildings,
            'task': self.task.id,
        }

    @staticmethod
    def update_locks():
        timeout = func.make_interval(0, 0, 0, 0, 0, 0, TaskLock.timeout)
        expired = TaskLock.query.filter(datetime.now() - TaskLock.date > timeout)
        for lock in expired.all():
            lock.update_lock()
        
    def update_lock(self):
        if self.elapsed_time > self.timeout:
            self.history.text = str(TASK_LOCK_TIMEOUT)
            h = TaskHistory(
                user=OsmUser.system_bot(),
                action=TaskHistory.Action.AUTO_UNLOCKED.value,
                text=models.TaskLock.Action(self.action).name,
                buildings=self.buildings,
                addresses=self.addresses,
            )
            self.task.history.append(h)
            db.session.delete(self)

    @property
    def elapsed_time(self):
        return int((datetime.now(tz=UTC) - self.date).total_seconds())

class StreetHistory(History):
    class Action(Enum):
        VALIDATED = 1
        RESET = 2

    id = db.Column(db.Integer, db.ForeignKey('history.id'), primary_key=True)
    street_id = db.Column(db.Integer, db.ForeignKey('street.id'), nullable=False)
    street = db.relationship('Street', back_populates='history')
    name = db.Column(db.String, nullable=True)

    __mapper_args__ = {'polymorphic_identity': 'SH'}


class StreetLock(History):
    LOCKED = 0

    id = db.Column(db.Integer, db.ForeignKey('history.id'), primary_key=True)
    street_id = db.Column(db.Integer, db.ForeignKey('street.id'), nullable=False)
    street = db.relationship('Street', back_populates='lock')

    __mapper_args__ = {'polymorphic_identity': 'SL'}

    def __init__(self, *args, **kwargs):
        kwargs['action'] = StreetLock.LOCKED
        super(StreetLock, self).__init__(*args, **kwargs)
