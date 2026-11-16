from sqlalchemy import Enum
from db import db

class User(db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(Enum('admin', 'user', 'staff', name='user_role'), nullable=False)

    approval_status = db.Column(Enum('approved', 'pending', 'blacklist', name='approval_status'), nullable=False, default='approved')

    staff_profile = db.relationship('Staff', backref='user', uselist=False, cascade='all, delete-orphan')
