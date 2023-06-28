from enum import Enum

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
    id = db.Column(db.Integer, db.ForeignKey('history.id'), primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    task = db.relationship('Task', back_populates='history')

    __mapper_args__ = {'polymorphic_identity': 'T'}


class StreetHistory(History):
    class Action(Enum):
        LOCKED = 1
        VALIDATED = 2
        RESET = 3

    id = db.Column(db.Integer, db.ForeignKey('history.id'), primary_key=True)
    street_id = db.Column(db.Integer, db.ForeignKey('street.id'), nullable=False)
    street = db.relationship('Street', back_populates='history')
    name = db.Column(db.String, nullable=True)

    __mapper_args__ = {'polymorphic_identity': 'S'}
