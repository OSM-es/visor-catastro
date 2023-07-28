import json

from geoalchemy2.shape import to_shape
from sqlalchemy.types import TypeDecorator, VARCHAR
from sqlalchemy.ext.mutable import Mutable


class JSONEncodedDict(TypeDecorator):
    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class MutableDict(Mutable, dict):
    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableDict):
            if isinstance(value, dict):
                return MutableDict(value)
            return Mutable.coerce(key, value)
        else:
            return value

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        self.changed()

class MutableList(Mutable, list):
    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            return Mutable.coerce(key, value)
        else:
            return value

    def __setitem__(self, key, value):
        list.__setitem__(self, key, value)
        self.changed()

    def __delitem__(self, key):
        list.__delitem__(self, key)
        self.changed()

def get_by_area(model, geom, percentaje=0.9, buffer=0):
    shape = to_shape(geom).buffer(buffer)
    candidates = []
    for c in model.query.filter(model.geom.intersects(geom)).all():
        s = to_shape(c.geom).buffer(0)
        if s.area:
            area = shape.intersection(s).area / s.area
            if area > percentaje:
                candidates.append({'area': area, 'feat': c})
    candidates.sort(key=lambda c: c['area'], reverse=True)
    return [c['feat'] for c in candidates]
