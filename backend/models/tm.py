from enum import Enum
from geoalchemy2 import Geometry

from config import Config
from models import db

MIGRATE = Config.MIGRATE_PATH


task_tmtask = db.Table(
    'task_tmtask',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id')),
    db.Column('tmtask_id', db.Integer, db.ForeignKey('tmtask.id')),
)


class TMTask(db.Model):
    __tablename__ = 'tmtask'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('tmproject.id'), nullable=True)
    muncode = db.Column(db.String)
    status = db.Column(db.String)
    filename = db.Column(db.String)
    geom = db.Column(Geometry("MultiPolygon", srid=4326))

    def get_path(self):
        fp = MIGRATE + self.muncode
        if self.filename:
            fp = fp + '/' + self.filename
        return fp


class TMProject(db.Model):
    __tablename__ = 'tmproject'

    class Status(Enum):
        DOWNLOADING = 0  # Pendiente de descarga.
        PUBLISHED = 1  # Disponible para migrar.
        MIGRATED = 2  # Migrado.

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    status = db.Column(db.Integer, default=Status.DOWNLOADING.value)
    addresses = db.Column(db.Boolean)
    buildings = db.Column(db.Boolean)
    created = db.Column(db.Date)
