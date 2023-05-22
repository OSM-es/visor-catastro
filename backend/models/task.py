from enum import Enum

from geoalchemy2 import Geometry, Index

from models import db


class TaskStatus(Enum):
    READY_FOR_ADDRESSES = 0
    LOCKED_FOR_ADDRESSES = 1
    READY_FOR_MAPPING = 2
    LOCKED_FOR_MAPPING = 3
    MAPPED = 4
    LOCKED_FOR_VALIDATION = 5
    VALIDATED = 6
    INVALIDATED = 7
    BLOCKED_BY_SYSTEM = 8
    NEED_UPDATE = 9


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    muncode = db.Column(db.String, index=True)
    localId = db.Column('localid', db.String, index=True)
    zone = db.Column(db.String)
    type = db.Column(db.String)
    parts = db.Column(db.Integer)
    status = db.Column(db.Integer, default=TaskStatus.READY_FOR_ADDRESSES.value)
    geom = db.Column(Geometry("GEOMETRYCOLLECTION", srid=4326))
    __table_args__ = (Index('codes_index', 'localid', 'muncode'), )

    @staticmethod
    def get_by_code(mun_code, local_id):
        return Task.query.filter(Task.muncode == mun_code, Task.localId == local_id).one_or_none()

    def __str__(self):
        return f"{self.muncode} {self.localId} {self.type} {self.parts}"

    def asdict(self):
        return {
            'id': self.id,
            'localId': self.localId,
            'muncode': self.muncode,
            'type': self.type,
            'parts': self.parts,
            'status': self.status,
        }