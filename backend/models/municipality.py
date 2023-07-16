from geoalchemy2 import Geometry

from models import db
from models.utils import JSONEncodedDict, MutableList, get_by_area


class Municipality(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    muncode = db.Column(db.String, index=True, unique=True)
    name = db.Column(db.String, nullable=False)
    src_date = db.Column(db.Date, nullable=False)
    geom = db.Column(Geometry("GEOMETRYCOLLECTION", srid=4326))
    update_id = db.Column(db.Integer, db.ForeignKey('municipality_update.id'), nullable=True)
    update = db.relationship('MunicipalityUpdate', back_populates='municipality', uselist=False)

    def asdict(self):
        return {
            'muncode': self.muncode,
            'name': self.name,
            'lock': self.update_id is not None,
        }

    @staticmethod
    def get_by_code(mun_code):
        return Municipality.query.filter(Municipality.muncode == mun_code).one_or_none()

    @staticmethod
    def get_by_area(geom):
        return get_by_area(Municipality, geom)

    def __str__(self):
        return f"{self.muncode} {self.name}"

    def set_lock():
        # TODO: si no hay ninguna tarea bloqueada
        # y no hay ninguna tarea invalidada
        # bloquea municipio
        # Devuelve estado bloqueo
        # si hay tarea invalidada, sería bueno un correo avisando
        pass


class MunicipalityUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    muncode = db.Column(db.String, index=True, unique=True)
    name = db.Column(db.String, nullable=False)
    src_date = db.Column(db.Date, nullable=False)
    geom = db.Column(Geometry("GEOMETRYCOLLECTION", srid=4326))
    municipality = db.relationship('Municipality', back_populates='update', uselist=False)

    def do_update(self):
        mun = self.municipality
        mun.muncode = self.muncode
        mun.name = self.name
        mun.src_date = self.src_date
        mun.geom = self.geom
        mun.lock = None
        mun.update = None
