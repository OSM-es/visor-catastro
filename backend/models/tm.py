from enum import Enum
from geoalchemy2 import Geometry

from config import Config
from models import db

MIGRATE = Config.MIGRATE_PATH


task_tmtask = db.Table(
    'task_tmtask',
    db.Column('task_id', db.Integer, db.ForeignKey('task.id')),
    db.Column('tmproject_id', db.Integer),
    db.Column('tmtask_id', db.Integer),
    db.ForeignKeyConstraint(
        ['tmproject_id', 'tmtask_id'],
        ['tmtask.project_id', 'tmtask.id'],
        name='tmtasks_fkey'
    )
)


class TMTask(db.Model):
    __tablename__ = 'tmtask'

    project_id = db.Column(
        db.Integer, db.ForeignKey('tmproject.id'), primary_key=True
    )
    id = db.Column(db.Integer, primary_key=True)
    muncode = db.Column(db.String)
    status = db.Column(db.String)
    filename = db.Column(db.String)
    geom = db.Column(Geometry("MultiPolygon", srid=4326))
    project = db.relationship('TMProject')

    def get_path(self):
        fp = MIGRATE + self.muncode
        if self.filename:
            fp = fp + '/' + self.filename
        return fp
    
    def asdict(self):
        return {
            'project_id': self.project_id,
            'id': self.id,
            'status': self.status,
        }


class TMProject(db.Model):
    __tablename__ = 'tmproject'

    class Status(Enum):
        DOWNLOADING = 0  # Pendiente de descarga.
        DOWNLOADED = 1  # Descarga realizada.
        PUBLISHED = 2  # Disponible para migrar.
        MIGRATED = 3  # Migrado.

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    status = db.Column(db.Integer, default=Status.DOWNLOADING.value)
    addresses = db.Column(db.Boolean)
    buildings = db.Column(db.Boolean)
    created = db.Column(db.Date)
