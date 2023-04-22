from models import db


class Municipality(db.Model):
    muncode = db.Column(db.String, primary_key=True)
    name = db.Column(db.String)

    def __str__(self):
        return f"{self.muncode} {self.name}"