from enum import Enum

from flask import current_app

from models import db
from models.utils import JSONEncodedDict, MutableDict


class OsmUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String, nullable=False)
    img = db.Column(db.String)
    user = db.relationship(
        'User',
        primaryjoin='or_(OsmUser.id==User.osm_id, OsmUser.id==User.import_id)',
        viewonly=True,
        uselist=False,
    )
    history = db.relationship('History', back_populates='user')

    def isStated(self):
        return 'import' in self.display_name or 'catastro' in self.display_name

    def asdict(self):
        return {
            'id': self.id,
            'display_name': self.display_name,
            'user': self.user.asdict() if self.user else None,
        }

    @staticmethod
    def system_bot():
        user = OsmUser.query.get(0)
        if not user:
            user = OsmUser(id=0, display_name='SystemBot')
            db.session.add(user)
            db.session.commit()
        return user


class User(db.Model):
    __table_args__ = (
        db.CheckConstraint('osm_id != import_id', name='ck_import_not_osm'),
    )

    class Role(Enum):
        READ_ONLY = -1
        MAPPER = 0
        ADMIN = 1

    class MappingLevel(Enum):
        BEGINNER = 1
        INTERMEDIATE = 2
        ADVANCED = 3

    id = db.Column(db.Integer, primary_key=True)
    locale = db.Column(db.String)
    role = db.Column(db.Integer, default=Role.READ_ONLY.value)
    tutorial = db.Column(
        MutableDict.as_mutable(JSONEncodedDict),
        default={'passed': [], 'next': 'login'},
    )
    mapping_level = db.Column(db.Integer, default=MappingLevel.BEGINNER.value)
    email = db.Column(db.String, nullable=True)
    osm_id = db.Column(
        db.Integer,
        db.ForeignKey('osm_user.id'),
        nullable=True,
        unique=True,
    )
    import_id = db.Column(
        db.Integer,
        db.ForeignKey('osm_user.id'),
        nullable=True,
        unique=True,
    )
    osm_user = db.relationship('OsmUser', foreign_keys=osm_id, back_populates='user')
    import_user = db.relationship('OsmUser', foreign_keys=import_id, back_populates='user')
    lock = db.relationship('TaskLock', back_populates='user', uselist=False)

    def asdict(self):
        return {
            'tutorial': self.tutorial,
            'email': self.email,
            'locale': self.locale,
            'role': User.Role(self.role).name,
            'mapping_level': User.MappingLevel(self.mapping_level).name,
            'osm_id': self.osm_id,
            'import_id': self.import_id,
        }

    def update_mapping_level(self, changeset_count):
        intermediate_level = current_app.config["MAPPER_LEVEL_INTERMEDIATE"]
        advanced_level = current_app.config["MAPPER_LEVEL_ADVANCED"]
        mapping_level = User.MappingLevel.BEGINNER.value
        if changeset_count > advanced_level:
            mapping_level = User.MappingLevel.ADVANCED.value
        elif intermediate_level < changeset_count < advanced_level:
            mapping_level = User.MappingLevel.INTERMEDIATE.value
        self.mapping_level = max(self.mapping_level, mapping_level)
