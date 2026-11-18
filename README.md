# Hi-Trek — Trek Management Application

Flask + Vue trek management with Admin, Trek Staff and Trekker roles, SQLite,
Redis caching, Celery reminders/reports and CSV export through local Mailpit.
Payments and refunds are simulated.

## Requirements

Install Python with pip/venv support, Node.js/npm, Redis and Mailpit.
The backend was checked with Python 3.14. The frontend requires Node.js
22.18+ within version 22, or 24.12+. Redis and Mailpit are separate programs.
The commands below are for Linux/macOS or a Linux terminal in WSL.

## Install and initialize

From the downloaded or cloned repository's root folder:

```bash
python3 -m venv backend/venv
backend/venv/bin/python -m pip install -r backend/requirements-milestone7.txt
backend/venv/bin/python backend/init_db.py
cd frontend
npm ci
cd ..
```

Keep all three `requirements-milestone*.txt` files: the last one references the
others. Initialization creates `backend/instance/users.db` and asks for an Admin
password. Log in as **admin@hi-trek.com** with that password. Running setup again
preserves the existing Admin account.

## Run the application

Run each process in a separate terminal. Paths below start from the repository
root. Reuse Redis or Mailpit if they are already running.

**Flask:**

```bash
backend/venv/bin/python backend/auth_app.py
```

**Vue:**

```bash
cd frontend
npx vite --config vite.auth.config.js --host 127.0.0.1 --port 5173 --strictPort
```

**Redis:**

```bash
redis-server
```

**Mailpit:**

```bash
mailpit
```

**Celery worker:**

```bash
cd backend
venv/bin/celery -A auth_app:celery worker --loglevel=info --pool=solo
```

**Celery Beat:**

```bash
cd backend
venv/bin/celery -A auth_app:celery beat --loglevel=info
```

Open **http://127.0.0.1:5173/auth.html#/login**. Use this host consistently for
login cookies. Open Mailpit at **http://127.0.0.1:8025** to view captured emails.
Mailpit receives SMTP on port 1025; it does not deliver to real inboxes.

The worker handles CSV exports and email jobs. Beat schedules daily reminders
at 08:00 and monthly Admin reports on day 1 at 09:00, Asia/Kolkata. Only one Beat
instance should run. CSV export requires Redis, the worker and Mailpit; it does
not require Beat. Stop each process with Ctrl+C.

Flask generates a signing secret on startup unless SECRET_KEY is supplied through
the environment. A restart with a new secret logs users out; log in again.
Do not commit real secrets.

## Optional demo data

After initialization, from the repository root:

```bash
backend/venv/bin/python backend/seed_demo.py
```

This adds 10 fictional trekkers, 10 staff, 10 treks and 16 bookings while preserving
existing records and Admin credentials. Upcoming demo treks start on or after
December 10, 2026. Read [the demo data guide](backend/DEMO_DATA.md) for account
credentials, dates and repeat-run behavior. Do not run it on unrelated production
data.

## Demonstrate the application

1. As Admin, create staff, create/approve a trek, assign staff and open bookings.
2. Register a trekker, log in, filter available treks and book places.
3. As assigned staff, manage capacity/participants and start/complete a trek.
4. As the trekker, view history and request a CSV export. Check Mailpit for the
   completion email and attachment.

From `backend`, with the worker running, trigger email jobs immediately:

```bash
venv/bin/celery -A auth_app:celery call tasks.send_daily_reminders
venv/bin/celery -A auth_app:celery call tasks.send_monthly_report
```

Reminders require confirmed bookings for upcoming treks starting tomorrow.
Reports summarize completed treks ending in the previous calendar month.

After opening a trek listing, inspect Redis caching:

```bash
redis-cli -n 2 --scan --pattern 'hi-trek:treks:*'
```

Use a returned key with `redis-cli -n 2 TTL 'key'`. Entries expire after five
minutes and are cleared after relevant changes. Cache failure falls back to
SQLite. Celery uses Redis databases 0 and 1; API caching uses database 2.

## Frontend build

```bash
cd frontend
npm run build -- --config vite.auth.config.js
```

The documented demonstration uses the development server. Production hosting is
not configured.

## Repository and submission

This repository retains the milestone structure: `backend/auth_app.py` and
`frontend/auth.html` are the application entry points. The app opens at login;
the older public marketing page is not included in the committed application.
A separately prepared submission ZIP is not part of this repository.

Exclude virtual environments, `node_modules`, generated builds, databases,
`__pycache__`, logs, `.env` secrets and Celery Beat files from submission archives.
Keep source files and dependency manifests. See the committed
[project report](24F2007142-MAD_II.pdf).

The eight `backend/MILESTONE_*.md` documents describe incremental development.
Use this README for the current setup; earlier milestone instructions describe
what was available at that stage.
