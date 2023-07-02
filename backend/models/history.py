from enum import Enum

from sqlalchemy.sql import expression

from models import db


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String, nullable=False)
    date = db.Column(db.DateTime, server_default=db.func.now(), index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('osm_user.id'), nullable=False)
    user = db.relationship('OsmUser', back_populates='history')
    action = db.Column(db.Integer, nullable=False)

    __mapper_args__ = {'polymorphic_on': 'type'}

    @property
    def target(self):
        return self.task if isinstance(self, TaskHistory) else self.street


class TaskHistory(History):
    class Action(Enum):
        LOCKED_FOR_MAPPING = 1
        MAPPED = 2
        LOCKED_FOR_VALIDATION = 3
        VALIDATED = 4
        INVALIDATED = 5
        NEED_UPDATE = 6

        @staticmethod
        def from_status(status):
            return TaskHistory.Action(status)

    lock_actions = [
        Action.LOCKED_FOR_MAPPING.value,
        Action.LOCKED_FOR_VALIDATION.value,
    ]

    id = db.Column(db.Integer, db.ForeignKey('history.id'), primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    task = db.relationship('Task', back_populates='history')
    buildings = db.Column(db.Boolean, nullable=False, server_default=expression.false())
    addresses = db.Column(db.Boolean, nullable=False, server_default=expression.false())

    __mapper_args__ = {'polymorphic_identity': 'TH'}


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
