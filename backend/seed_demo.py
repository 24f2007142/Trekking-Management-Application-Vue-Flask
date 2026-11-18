"""Create 10 fictional trekkers, 10 staff and 10 treks for a local demonstration.

Run init_db.py first, then: python seed_demo.py
Existing application data is preserved. Run again to keep the same demo records.
"""
import argparse
import sqlite3
from datetime import date, datetime, timedelta
from pathlib import Path

from flask import Flask
from werkzeug.security import generate_password_hash

from db import db
from models import User, Staff, Trek, Booking, StaffTrek

DEMO_PASSWORD = 'DemoTrek2026!'


def seed(database):
    database = Path(database).resolve()
    if not database.exists():
        raise RuntimeError('Run init_db.py first to create the database and Admin.')

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + str(database)
    db.init_app(app)

    with app.app_context():
        try:
            if not User.query.filter_by(role='admin').first():
                raise RuntimeError('Run init_db.py first to create Admin.')

            emails = [f'{role}{number:02d}@demo.example.test'
                      for role in ('trekker', 'staff') for number in range(1, 11)]
            existing_accounts = User.query.filter(User.email.in_(emails)).count()
            existing_treks = Trek.query.filter(Trek.trek_name.like('[Demo] %')).count()
            if existing_accounts or existing_treks:
                if existing_accounts == 20 and existing_treks == 10:
                    print('Demo records already exist. Kept their current statuses and passwords.')
                    return
                raise RuntimeError('Some demo names already exist. No data changed; use a fresh demo database.')

            # Save a copy before inserting records. Nothing is deleted or reset.
            stamp = datetime.now().strftime('%Y%m%d-%H%M%S-%f')
            backup = database.with_name(database.name + '.before-demo-' + stamp + '.bak')
            with sqlite3.connect(database) as source, sqlite3.connect(backup) as target:
                source.backup(target)

            trekkers = []
            guides = []
            for number in range(1, 11):
                # 8 active accounts, 1 awaiting approval, 1 blacklisted per role.
                status = 'approved' if number <= 8 else ('pending' if number == 9 else 'blacklist')
                user = User(username=f'Demo Trekker {number:02d}', email=emails[number - 1],
                            password=generate_password_hash(DEMO_PASSWORD), role='user',
                            approval_status=status)
                guide = User(username=f'Demo Staff {number:02d}', email=emails[number + 9],
                             password=generate_password_hash(DEMO_PASSWORD), role='staff',
                             approval_status=status)
                guide.staff_profile = Staff(contact_number=f'00000000{number:02d}')
                trekkers.append(user)
                guides.append(guide)
                db.session.add_all([user, guide])

            # name, location, difficulty, duration, start, lifecycle, open, capacity
            definitions = [
                ('Open Easy Walk', 'Yelagiri', 'easy', 1, '2026-12-10', 'upcoming', True, 10),
                ('Open Mountain Trail', 'Munnar', 'moderate', 2, '2026-12-12', 'upcoming', True, 8),
                ('Full Summit Trek', 'Manali', 'hard', 3, '2026-12-15', 'upcoming', True, 3),
                ('Closed Forest Trail', 'Coorg', 'moderate', 2, '2026-12-19', 'upcoming', False, 8),
                ('Awaiting Approval', 'Ooty', 'easy', 1, '2026-12-22', 'pending', False, 12),
                ('Approved Ridge Trek', 'Wayanad', 'hard', 2, '2026-12-24', 'approved', False, 10),
                ('In Progress Valley', 'Kodaikanal', 'moderate', 3, '2026-11-18', 'ongoing', False, 8),
                ('Completed Lake Walk', 'Yercaud', 'easy', 1, '2026-10-10', 'completed', False, 10),
                ('Completed Peak Trek', 'Munnar', 'hard', 2, '2026-10-20', 'completed', False, 10),
                ('Cancelled Coastal Walk', 'Gokarna', 'easy', 1, '2026-12-28', 'cancelled', False, 10),
            ]
            treks = []
            for number, row in enumerate(definitions):
                name, location, difficulty, duration, start, status, opened, capacity = row
                start = date.fromisoformat(start)
                trek = Trek(trek_name='[Demo] ' + name, location=location, difficulty=difficulty,
                            duration=duration, start_date=start,
                            end_date=start + timedelta(days=duration - 1),
                            total_slots=capacity, booked_slots=0, price=500 + number * 250,
                            bookings_open=opened, trek_status=status,
                            staffing_status='pending', description='Fictional viva demonstration record.')
                treks.append(trek)
                db.session.add(trek)
            db.session.flush()

            # Staff 8 is active but unassigned. Staff 9/10 cannot log in.
            # Staff 1 has a past completed assignment and a future assignment.
            for trek_number, staff_number in [(1, 1), (2, 2), (3, 3), (4, 4),
                                              (6, 5), (7, 6), (8, 7), (9, 1), (10, 2)]:
                trek = treks[trek_number - 1]
                state = trek.trek_status if trek.trek_status in ('completed', 'cancelled') else 'assigned'
                db.session.add(StaffTrek(staff_id=guides[staff_number - 1].staff_profile.id,
                                        trek_id=trek.id, status=state))
                trek.staffing_status = 'pending' if state == 'cancelled' else 'assigned'

            # trek, trekker, places, booking status, payment status, removed by staff
            bookings = [
                (1, 1, 1, 'confirmed', 'successful', None),
                (1, 2, 2, 'confirmed', 'successful', None),
                (1, 3, 1, 'cancelled', 'refund finished', None),
                (2, 3, 2, 'confirmed', 'successful', None),
                (2, 4, 1, 'cancelled', 'refund initiated', 'Demo Staff 02'),
                (3, 5, 1, 'confirmed', 'successful', None),
                (3, 6, 2, 'confirmed', 'successful', None),
                (4, 7, 1, 'confirmed', 'successful', None),
                (7, 1, 1, 'confirmed', 'successful', None),
                (7, 2, 2, 'confirmed', 'successful', None),
                (8, 1, 2, 'completed', 'successful', None),
                (8, 3, 1, 'completed', 'successful', None),
                (9, 4, 1, 'completed', 'successful', None),
                (9, 5, 3, 'completed', 'successful', None),
                (10, 6, 1, 'cancelled', 'refund finished', None),
                (10, 7, 2, 'cancelled', 'refund finished', None),
            ]
            for trek_number, user_number, places, status, payment, removed_by in bookings:
                trek = treks[trek_number - 1]
                db.session.add(Booking(user_id=trekkers[user_number - 1].id, trek_id=trek.id,
                    booking_date=min(date(2026, 11, 18), trek.start_date - timedelta(days=7)),
                    status=status, slots_booked=places, payment_status=payment,
                    removed_by_staff_name=removed_by))
                if status in ('confirmed', 'completed'):
                    trek.booked_slots += places

            db.session.commit()
            print('Created 10 trekkers, 10 staff, 10 treks and 16 bookings.')
            print('Backup:', backup)
            print('Demo login: trekker01@demo.example.test or staff01@demo.example.test')
            print('Demo password:', DEMO_PASSWORD)
            print('Admin and existing records were preserved. Cached listings may take five minutes to refresh.')
        except Exception:
            db.session.rollback()
            raise
        finally:
            db.session.remove()
            db.engine.dispose()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path,
                        default=Path(__file__).resolve().parent / 'instance' / 'users.db')
    seed(parser.parse_args().database)
