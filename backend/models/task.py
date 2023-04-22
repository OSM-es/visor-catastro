from geoalchemy2 import Geometry

from models import db
from models.status import TaskStatus


class Task(db.Model):
    muncode = db.Column(db.String, primary_key=True)
    localId = db.Column(db.String, primary_key=True)
    zone = db.Column(db.String)
    type = db.Column(db.String)
    parts = db.Column(db.Integer)
    task_status = db.Column(db.Integer, default=TaskStatus.READY.value)
    geom = db.Column(Geometry("MULTIPOLYGON", srid=4326))

    def __str__(self):
        return f"{self.muncode} {self.localId} {self.type} {self.parts}"