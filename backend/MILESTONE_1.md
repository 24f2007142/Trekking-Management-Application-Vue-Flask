# Milestone 1: Database models and schema

This milestone runs independently of the API, Vue, Redis and Celery.

## Setup

From the repository root, with Python 3.10 or newer:

```bash
python3 -m venv backend/venv
backend/venv/bin/python -m pip install -r backend/requirements-milestone1.txt
backend/venv/bin/python backend/init_db.py
```

If the virtual environment already exists, skip its creation.

The script follows five steps: 
- connect to SQLite 
- create the tables
- check for an existing Admin 
- hash the password 
- save the Admin account. 

It asks for a password without displaying what you type. The Admin email is `admin@hi-trek.com`. Passwords are stored as hashes. No password is committed to Git.

The database is `backend/instance/users.db`, matching the web app's SQLite location. Running the script again keeps the existing Admin and password.
No command-line options are needed.

This creates missing tables; it does not migrate existing tables. Use a fresh
database to evaluate this milestone independently. Do not commit database files.

## Schema

| Model/table | Purpose and relationships |
| --- | --- |
| User / users | Admin, staff and trekker accounts; one-to-many bookings and one-to-one staff profile |
| Staff / staff | Staff contact and availability; belongs to a User |
| Trek / treks | Name, location, difficulty, duration, dates, capacity, price and lifecycle |
| Booking / bookings | User/Trek foreign keys, booking date, status, payment and reserved places |
| StaffTrek / staff_trek | Association linking staff and treks with assignment status |

Available slots are calculated as total slots minus booked slots. The `user` role
means Trekker. Booking availability is represented by `bookings_open` alongside
the trek lifecycle. All models are registered by `models/__init__.py`.