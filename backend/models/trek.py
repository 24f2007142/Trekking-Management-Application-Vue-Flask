from db import db
from sqlalchemy import Enum


class Trek(db.Model):

    __tablename__ = 'treks'

    id = db.Column(db.Integer, primary_key=True)

    trek_name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(Enum('easy', 'moderate', 'hard', name='difficulty_level'), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    total_slots = db.Column(db.Integer, nullable=False)
    booked_slots = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Float, nullable=False)
    bookings_open = db.Column(db.Boolean, nullable=False, default=True)
    description = db.Column(db.String(100))

    trek_status = db.Column(Enum('pending', 'approved', 'upcoming', 'ongoing', 'completed', 'cancelled', name='trek_status'), nullable=False, default='upcoming')
    staffing_status = db.Column(Enum('pending', 'assigned', name='staffing_status'), nullable=False, default='pending')

    booking = db.relationship('Booking', backref='trek')
    staff_assignments = db.relationship('StaffTrek', back_populates='trek', cascade='all, delete-orphan')

    @property
    def display_id(self):
        return f"T{self.id:03d}"

