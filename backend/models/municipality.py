from models import db


class Municipality(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    muncode = db.Column(db.String, index=True)
    name = db.Column(db.String)

    def __str__(self):
        return f"{self.muncode} {self.name}"