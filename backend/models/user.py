from enum import Enum

from models import db
from models.utils import JSONEncodedDict, MutableDict


class OsmUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String, nullable=False)
    user = db.relationship(
        'User',
        primaryjoin='or_(OsmUser.id==User.osm_id, OsmUser.id==User.import_id)',
        viewonly=True,
        uselist=False,
    )

    def isStated(self):
        return 'import' in self.display_name or 'catastro' in self.display_name

    def asdict(self):
        return {
            'id': self.id,
            'display_name': self.display_name,
            'user': self.user.asdict() if self.user else None,
        }


class User(db.Model):
    __table_args__ = (
        db.CheckConstraint('osm_id != import_id', name='ck_import_not_osm'),
    )

    class Role(Enum):
        READ_ONLY = -1
        MAPPER = 0
        ADMIN = 1

    id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.Integer, default=Role.READ_ONLY.value)
    tutorial = db.Column(
        MutableDict.as_mutable(JSONEncodedDict),
        default={'passed': [], 'next': 'login'},
    )
    email = db.Column(db.String, nullable=True)
    osm_id = db.Column(db.Integer, db.ForeignKey('osm_user.id'), nullable=True)
    import_id = db.Column(db.Integer, db.ForeignKey('osm_user.id'), nullable=True)
    osm_user = db.relationship('OsmUser', foreign_keys=osm_id, back_populates='user')
    import_user = db.relationship('OsmUser', foreign_keys=import_id, back_populates='user')


    def asdict(self):
        return {
            'tutorial': self.tutorial,
            'email': self.email,
            'role': User.Role(self.role).name,
            'osm_id': self.osm_id,
            'import_id': self.import_id,
        }