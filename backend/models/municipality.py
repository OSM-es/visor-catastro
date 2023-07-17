from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape, to_shape

from models import db
from models.utils import get_by_area
import models


class Municipality(db.Model):

    class Update(db.Model):
        __tablename__ = 'municipality_update'

        id = db.Column(db.Integer, primary_key=True)
        muncode = db.Column(db.String, index=True, unique=True, nullable=True)
        name = db.Column(db.String, nullable=True)
        src_date = db.Column(db.Date, nullable=True)
        geom = db.Column(Geometry("GEOMETRYCOLLECTION", srid=4326))
        municipality = db.relationship('Municipality', back_populates='update', uselist=False)

        def set(self, muncode, name, src_date, shape):
            self.muncode = muncode
            self.name = name
            self.src_date = src_date
            self.geom = from_shape(shape)

        def do_update(self):
            mun = self.municipality
            mun.muncode = self.muncode
            mun.name = self.name
            mun.src_date = self.src_date
            mun.geom = self.geom
            mun.lock = None
            mun.update = None


    id = db.Column(db.Integer, primary_key=True)
    muncode = db.Column(db.String, index=True, unique=True)
    name = db.Column(db.String, nullable=False)
    src_date = db.Column(db.Date, nullable=False)
    geom = db.Column(Geometry("GEOMETRYCOLLECTION", srid=4326))
    update_id = db.Column(db.Integer, db.ForeignKey('municipality_update.id'), nullable=True)
    update = db.relationship(Update, back_populates='municipality', uselist=False)

    def asdict(self):
        return {
            'muncode': self.muncode,
            'name': self.name,
            'lock': self.update_id is not None,
        }

    @staticmethod
    def create(muncode, name, src_date, geom):
        mun = Municipality(
            muncode=muncode, name=name, src_date=src_date, geom=geom
        )
        db.session.add(mun)
        return mun        

    @staticmethod
    def get_by_code(mun_code):
        return Municipality.query.filter(Municipality.muncode == mun_code).one_or_none()

    @staticmethod
    def get_match(mun_code, mun_name, src_date, shape):
        geom = from_shape(shape)
        candidates = [
            c for c in get_by_area(Municipality, geom)
            if c.update_id is None
        ]
        if candidates:
            mun = next(
                (c for c in candidates if c.muncode == mun_code),
                candidates[0]
            )
        else:
            mun = Municipality.create(mun_code, mun_name, src_date, geom)
        return mun, candidates

    def set_lock(self):
        locks = models.Task.query.filter(models.Task.lock_id != None).count()
        if locks == 0:
            self.update = Municipality.Update()
        return locks == 0

    def equal(self, shape):
        mun_shape = to_shape(self.geom)
        intersect = shape.intersection(mun_shape).area
        return (
            intersect / mun_shape.area > 0.9
            and intersect / shape.area > 0.9
        )

    def __str__(self):
        return f"{self.muncode} {self.name}"
