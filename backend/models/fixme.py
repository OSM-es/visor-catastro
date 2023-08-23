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
        CA2O_PART_BIGGER = 0  # Parte mayor que edificio
        CA2O_SMALL_AREA = 1  # Área demasiado pequeña
        CA2O_BIG_AREA = 2  # Área demasiado grande
        CA2O_MISSING_PARTS = 3  # Partes no cubren edificio
        CA2O_GEOS = 4  # Error de validación GEOS
        UPDATE_DEL = 5  # Eliminar
        UPDATE_ADD = 6  # Añadir
        UPDATE_TAGS = 7  # Han cambiado las etiquetas
        UPDATE_GEOM = 8  # Ha cambiado la geometría
        UPDATE_FULL = 9  # Cambian tanto etiquetas como geometría
        UPDATE_DEL_CHECK = 10  # Comprobar si hay que eliminar

        @staticmethod
        def from_ca2o(msg):
            _type = None
            if msg == 'Esta parte es mayor que su edificio':
                _type = Fixme.Type.CA2O_PART_BIGGER
            elif msg == 'Comprobar, área demasiado pequeña':
                _type = Fixme.Type.CA2O_SMALL_AREA
            elif msg == 'Comprobar, área demasiado grande':
                _type = Fixme.Type.CA2O_BIG_AREA
            elif msg == 'Las partes de edificio no cubren todo el contorno':
                _type = Fixme.Type.CA2O_MISSING_PARTS
            elif 'Validación GEOS' in msg:
                _type = Fixme.Type.CA2O_GEOS
            return _type

        def is_update(self):
            return self.name.startswith('UPDATE')

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Integer)
    src_date = db.Column(db.Date, nullable=False)
    text = db.Column(db.String)
    validated = db.Column(db.Boolean)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=True)
    task = db.relationship('Task', back_populates='fixmes')
    geom = db.Column(Geometry("POINT", srid=4326))

    def __str__(self):
        shape = to_shape(self.geom)
        return f"{shape} {self.type} {self.text}"

    def to_feature(self):
        shape = to_shape(self.geom)
        data = {
            'id': self.id,
            'type': Fixme.Type(self.type).name,
            'fixme': self.text,
            'validated': self.validated,
        }
        return osm2geojson.shape_to_feature(shape, data)

    def is_update(self):
        return Fixme.Type(self.type).is_update()
