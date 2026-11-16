from getpass import getpass

from flask import Flask
from werkzeug.security import generate_password_hash

from db import db
from models import User


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

if __name__ == '__main__':


    with app.app_context():
        
        db.create_all()
        print('Database tables are ready.')

       
        admin_user = User.query.filter_by(role='admin').first()

        if admin_user:
            print('Admin already exists. Skipping setup.')
        else:
            
            password = getpass('Enter a password for Admin: ')
            while not password.strip():
                password = getpass('Password cannot be empty. Enter a password: ')

            admin = User(
                username='Admin',
                email='admin@hi-trek.com',
                password=generate_password_hash(password),
                role='admin',
                approval_status='approved'
            )

            
            db.session.add(admin)
            db.session.commit()
            print('Admin created! Log in with admin@hi-trek.com and your password.')
