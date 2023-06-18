from enum import Enum

from models import db


class Street(db.Model):
    class Source(Enum):
        CAT = 0
        OSM = 1

    id = db.Column(db.Integer, primary_key=True)
    mun_code = db.Column(db.String, index=True)
    cat_name = db.Column(db.String, index=True)
    osm_name = db.Column(db.String, index=True)
    source = db.Column(db.Integer)
    name = db.Column(db.String)

    def asdict(self):
        return {
            'mun_code': self.mun_code,
            'cat_name': self.cat_name,
            'osm_name': self.osm_name,
            'source': Street.Source(self.source).name,
            'name': self.name,
        }