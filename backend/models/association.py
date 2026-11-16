from db import db


class StaffTrek(db.Model):

    __tablename__ = 'staff_trek'

    id = db.Column(db.Integer, primary_key=True)

    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('treks.id'), nullable=False)
    status = db.Column(
    db.Enum(
        'assigned',
        'cancelled',
        'completed',
        name='assignment_status'
    ),
    nullable=False,
    default='assigned'
)

    staff = db.relationship('Staff', back_populates='trek_assignments')
    trek = db.relationship('Trek', back_populates='staff_assignments')

