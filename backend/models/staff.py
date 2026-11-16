from db import db

class Staff(db.Model):

    __tablename__ = 'staff'

    id = db.Column(db.Integer, primary_key=True)

    contact_number = db.Column(db.String(15), nullable=False)
    next_available_date = db.Column(db.Date)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)

    trek_assignments = db.relationship('StaffTrek', back_populates='staff', cascade='all, delete-orphan')
