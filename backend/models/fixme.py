from enum import Enum

from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
import osm2geojson

from models import db


class Fixme(db.Model):
    """Una anotación a una tarea. Requiere ser revisada por el editor.
    Puede ser introducida por el programa de conversión o para actualizar 
    los datos.
    """

    class Type(Enum):
        CONVERTER = 0  # Introducida por catatom2osm
        UPDATE_DEL = 1  # Eliminar
        UPDATE_ADD = 2  # Añadir
        UPDATE_TAGS = 3  # Han cambiado las etiquetas
        UPDATE_GEOM = 4  # Ha cambiado la geometría
        UPDATE_FULL = 5  # Cambian tanto etiquetas como geometría

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer)
    src_date = db.Column(db.Date, nullable=False)
    text = db.Column(db.String)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True)
    task = db.relationship('Task', back_populates='fixmes')
    geom = db.Column(Geometry("POINT", srid=4326))

    def __str__(self):
        shape = to_shape(self.geom)
        return f"{shape} {self.text}"

    def to_feature(self):
        shape = to_shape(self.geom)
        return osm2geojson.shape_to_feature(shape, {'fixme': self.text})
   