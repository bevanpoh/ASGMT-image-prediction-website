from application import db


class CifarPredictionEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_on = db.Column(db.DateTime, nullable=False)

    filename = db.Column(db.String(255))
    filepath = db.Column(db.String(255))
    prediction = db.Column(db.String(50))
    model = db.Column(db.String(50))

    contrast = db.Column(db.Integer)
    sharpen = db.Column(db.Float)
