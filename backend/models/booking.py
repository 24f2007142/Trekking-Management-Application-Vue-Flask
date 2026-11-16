from db import db
from sqlalchemy import Enum

class Booking(db.Model):

    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)


    booking_date = db.Column(db.Date, nullable=False)
    status = db.Column(Enum('pending', 'confirmed', 'cancelled', 'completed', default='confirmed', name='booking_status'), nullable=False, default='pending')
    payment_status = db.Column(db.String(30), nullable=False, default='successful')
    removed_by_staff_name = db.Column(db.String(100))

    slots_booked = db.Column(db.Integer, nullable=False, default=1)

    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User', backref='bookings')
