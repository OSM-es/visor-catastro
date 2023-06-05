from geoalchemy2 import Geometry

from models import db


class Province(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provcode = db.Column(db.String, index=True)
    name = db.Column(db.String, nullable=False)
    geom = db.Column(Geometry("GEOMETRYCOLLECTION", srid=4326))

    @staticmethod
    def get_by_code(prov_code):
        return Province.query.filter(Province.provcode == prov_code).one_or_none()

    def __str__(self):
        return f"{self.provcode} {self.name}"
