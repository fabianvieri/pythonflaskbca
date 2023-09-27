from extensions import db


class Room(db.Model):
    room_id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(255), nullable=False)
    price_per_night = db.Column(db.Float, nullable=False)
    availibility = db.Column(db.Boolean, nullable=False)
