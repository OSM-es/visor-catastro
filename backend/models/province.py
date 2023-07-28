from geoalchemy2 import Geometry

from models import db, Task


class Province(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    provcode = db.Column(db.String, index=True)
    name = db.Column(db.String, nullable=False)
    task_count = db.Column(db.Integer, nullable=True)
    geom = db.Column(Geometry("GEOMETRYCOLLECTION", srid=4326))
    centre = db.Column(Geometry("POINT", srid=4326))

    @staticmethod
    def get_by_code(prov_code):
        return Province.query.filter(Province.provcode == prov_code).one_or_none()

    @staticmethod
    def count_tasks():
        for prov in Province.query.all():
            prov.task_count = Task.query_by_provcode(prov.provcode).count()

    def __str__(self):
        return f"{self.provcode} {self.name}"
