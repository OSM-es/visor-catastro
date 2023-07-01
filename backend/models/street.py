from datetime import datetime
from enum import Enum

from sqlalchemy.sql import expression

from models import db, StreetHistory, StreetLock

STREET_LOCK_TIMEOUT = 3600


class Street(db.Model):
    class Source(Enum):
        CAT = 0
        OSM = 1

    id = db.Column(db.Integer, primary_key=True)
    mun_code = db.Column(db.String, index=True)
    cat_name = db.Column(db.String, index=True)
    osm_name = db.Column(db.String, index=True)
    source = db.Column(db.Integer)
    validated = db.Column(db.Boolean, nullable=False, server_default=expression.false())
    history = db.relationship('StreetHistory', back_populates='street')
    lock = db.relationship('StreetLock', back_populates='street', uselist=False)
    name = db.Column(db.String)

    @staticmethod
    def get_by_name(mun_code, name):
        return Street.query.filter(Street.mun_code == mun_code, Street.cat_name == name).one_or_none()

    def asdict(self):
        return {
            'mun_code': self.mun_code,
            'cat_name': self.cat_name,
            'osm_name': self.osm_name,
            'validated': self.validated,
            'source': Street.Source(self.source).name,
            'name': self.name,
            'is_locked': self.is_locked(),
            'owner': self.owner.asdict() if self.owner else None,
        }
    
    def is_locked(self):
        if self.lock:
            age = (datetime.now() - self.lock.date).total_seconds()
            if age < STREET_LOCK_TIMEOUT:
                return True
            self.unlock()
        return False

    def unlock(self):
        db.session.delete(self.lock)
        db.session.commit()

    def set_lock(self, user):
        self.lock = StreetLock(user=user)
        db.session.add(self)
        db.session.commit()

    @property
    def owner(self):
        if self.lock:
            return self.lock.user
        return None

    def add_history(self, user):
        action = StreetHistory.Action.VALIDATED.value if self.validated else StreetHistory.Action.RESET.value
        self.history.append(StreetHistory(user=user, action=action, name=self.name))
