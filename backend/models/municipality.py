from geoalchemy2 import Geometry

from models import db, utils
from models.utils import JSONEncodedDict, MutableList


class Municipality(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    muncode = db.Column(db.String, index=True, unique=True)
    name = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, nullable=False)
    geom = db.Column(Geometry("GEOMETRYCOLLECTION", srid=4326))
    lock = db.Column(db.Boolean)
    tasks = db.relationship('Task', back_populates='municipality')


    @staticmethod
    def get_by_code(mun_code):
        return Municipality.query.filter(Municipality.muncode == mun_code).one_or_none()

    @staticmethod
    def get_by_area(geom):
        return utils.get_by_area(Municipality, geom)

    def __str__(self):
        return f"{self.muncode} {self.name}"

    def lock():
        # TODO: si no hay ninguna tarea bloqueada
        # y no hay ninguna tarea invalidada
        # bloquea municipio
        # Devuelve estado bloqueo
        # si hay tarea invalidada, sería bueno un correo avisando
        pass


    class Update(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        muncode = db.Column(db.String, index=True, unique=True)
        name = db.Column(db.String, nullable=True)
        date = db.Column(db.Date, nullable=True)
        uploaded = db.Column(db.Boolean)
        childs = db.Column(MutableList.as_mutable(JSONEncodedDict), default=[])
        brothers = db.Column(MutableList.as_mutable(JSONEncodedDict), default=[])
        geom = db.Column(Geometry("GEOMETRYCOLLECTION", srid=4326))


        @staticmethod
        def get_by_code(mun_code):
            return Update.query.filter(Update.muncode == mun_code).one_or_none()
