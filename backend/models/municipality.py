from glob import glob
from pathlib import Path
from enum import Enum
import os
import re
import shutil

from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape, to_shape

from models import db
from models.utils import get_by_area
import models
from config import Config

UPDATE = Config.UPDATE_PATH
DIST = Config.DIST_PATH
BACKUP = Config.BACKUP_PATH


class Municipality(db.Model):

    class Status(Enum):
        READY = 0
        MAPPING = 1
        MAPPED = 2
        VALIDATED = 3

    class Update(db.Model):
        __tablename__ = 'municipality_update'

        id = db.Column(db.Integer, primary_key=True)
        muncode = db.Column(db.String, index=True, unique=True, nullable=True)
        name = db.Column(db.String, nullable=True)
        src_date = db.Column(db.Date, nullable=True)
        geom = db.Column(Geometry("GEOMETRYCOLLECTION", srid=4326))
        municipality = db.relationship('Municipality', back_populates='update', uselist=False)

        @staticmethod
        def get_path(mun_code, filename=None):
            fp = UPDATE + mun_code
            if filename:
                fp = fp + '/' + filename
            return fp

        @staticmethod
        def clean():
            for p in os.listdir(UPDATE):
                if re.match(r'^\d{5}$', p):
                    shutil.rmtree(UPDATE + p)


        def path(self, filename=None):
            return Municipality.Update.get_path(self.muncode, filename)

        def set(self, muncode, name, src_date, shape):
            self.muncode = muncode
            self.name = name
            self.src_date = src_date
            self.geom = from_shape(shape)

        def do_update(self):
            mun = self.municipality
            mun.backup()
            mun.muncode = self.muncode
            mun.name = self.name
            mun.src_date = self.src_date
            mun.geom = self.geom
            mun.lock = None
            mun.update = None
            mun.publish()
            db.session.delete(self)


    id = db.Column(db.Integer, primary_key=True)
    muncode = db.Column(db.String, index=True, unique=True)
    name = db.Column(db.String, nullable=False)
    src_date = db.Column(db.Date, nullable=False)
    created = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    task_count = db.Column(db.Integer, nullable=True)
    geom = db.Column(Geometry("GEOMETRYCOLLECTION", srid=4326))
    update_id = db.Column(db.Integer, db.ForeignKey('municipality_update.id'), nullable=True)
    update = db.relationship(Update, back_populates='municipality', uselist=False)

    def asdict(self):
        return {
            'muncode': self.muncode,
            'name': self.name,
            'created': self.created.isoformat(),
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
    def query_by_prov(code):
        return Municipality.query.filter(Municipality.muncode.startswith(code))
        
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

    @staticmethod
    def get_path(mun_code, filename=None):
        fp = DIST + mun_code
        if filename:
            fp = fp + '/' + filename
        return fp

    def path(self, filename=None):
        return Municipality.get_path(self.muncode, filename)

    def set_lock(self):
        locks = models.Task.query.filter(models.Task.lock_id != None).count()
        if locks == 0 and self.update_id is None:
            self.update = Municipality.Update()
            self.update.muncode = self.muncode
            self.update.name = self.name
            self.update.src_date = self.src_date
            self.update.geom = self.geom
        return locks == 0

    def equal(self, shape):
        mun_shape = to_shape(self.geom)
        if not shape.intersects(mun_shape): return False
        intersect = shape.intersection(mun_shape).area
        return (
            intersect / mun_shape.area > 0.9
            and intersect / shape.area > 0.9
        )

    def delete(self):
        if self.lock:
            db.session.delete(self.lock)
        for h in models.StreetHistory.query.join(
            models.Street
        ).filter(
            models.Street.mun_code==self.muncode
        ).all():
            db.session.delete(h)
        models.Street.query_by_code(self.muncode).delete()
        self.backup()
        db.session.delete(self)
        h = models.History(action=models.History.Action.DEL_MUNICIPALITY.value)
        db.session.add(h)

    def backup(self):
        target = BACKUP + self.src_date.isoformat() + '/' + self.muncode
        if glob(f"{DIST}{self.muncode}/tasks/*.osm.gz"):
            shutil.move(DIST + self.muncode, target)
        else:
            shutil.rmtree(DIST + self.muncode)

    def publish(self):
        self.task_count = models.Task.query_by_muncode(self.muncode).count()
        Path(UPDATE, self.muncode, 'uploaded').touch()
        os.makedirs(DIST + self.muncode)
        for p in os.listdir(UPDATE + self.muncode):
            if p != 'uploaded':
                src = Path(UPDATE, self.muncode, p)
                dst = Path(DIST, self.muncode, p)
                shutil.move(src, dst)

    def __str__(self):
        return f"{self.muncode} {self.name}"
