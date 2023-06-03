from models import db


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
            'stated': self.isStated(),
        }


class User(db.Model):
    __table_args__ = (
        db.CheckConstraint('osm_id != import_id', name='ck_import_not_osm'),
    )

    id = db.Column(db.Integer, primary_key=True)
    tutorial = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    osm_id = db.Column(db.Integer, db.ForeignKey('osm_user.id'), nullable=True)
    import_id = db.Column(db.Integer, db.ForeignKey('osm_user.id'), nullable=True)
    osm_user = db.relationship('OsmUser', foreign_keys=osm_id, back_populates='user')
    import_user = db.relationship('OsmUser', foreign_keys=import_id, back_populates='user')


    def asdict(self):
        return {
            'id': self.id,
            'tutorial': self.tutorial,
            'email': self.email,
            'osm_id': self.osm_id,
            'import_id': self.import_id,
        }