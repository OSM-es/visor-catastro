from geoalchemy2 import Geometry

from models import db


class Municipality(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    muncode = db.Column(db.String, index=True)
    name = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, nullable=False)
    geom = db.Column(Geometry("GEOMETRYCOLLECTION", srid=4326))

    @staticmethod
    def get_by_code(mun_code):
        return Municipality.query.filter(Municipality.muncode == mun_code).one_or_none()

    def __str__(self):
        return f"{self.muncode} {self.name}"
