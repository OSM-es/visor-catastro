from geoalchemy2 import Geometry, Index

from models import db
from models.status import TaskStatus


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    muncode = db.Column(db.String)
    localId = db.Column('localid', db.String)
    zone = db.Column(db.String)
    type = db.Column(db.String)
    parts = db.Column(db.Integer)
    status = db.Column(db.Integer, default=TaskStatus.READY.value)
    geom = db.Column(Geometry("GEOMETRYCOLLECTION", srid=4326))
    __table_args__ = (Index('codes_index', 'localid', 'muncode'), )

    @staticmethod
    def get_by_code(mun_code, local_id):
        return Task.query.filter(Task.muncode == mun_code, Task.localId == local_id).one_or_none()

    def __str__(self):
        return f"{self.muncode} {self.localId} {self.type} {self.parts}"