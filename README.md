# Hi-Trek — Trek Management Application

Flask + Vue trek management with Admin, Trek Staff and Trekker roles, SQLite,
Redis caching, Celery reminders/reports and CSV export through local Mailpit.

## Submission and viva

The `submission/` folder is the self-contained source package with standard entry
points. Follow [its setup instructions](submission/README.md). It includes
`backend/app.py`, one `backend/requirements.txt`, and a frontend started with
`npm run dev`. The API contract is `submission/api.yaml`.

Generated environments, databases, dependency folders, builds and ZIPs are not
source files. Exclude them when packaging. The submission app opens at login;
the older public marketing page is not part of this version.

## Milestone development version

The root `backend/` and `frontend/` folders retain the original milestone history.
From the project root:

```bash
python3 -m venv backend/venv
backend/venv/bin/python -m pip install -r backend/requirements-milestone7.txt
backend/venv/bin/python backend/init_db.py
backend/venv/bin/python backend/auth_app.py
```

In another terminal:

```bash
cd frontend
npm ci
npx vite --config vite.auth.config.js --host 127.0.0.1
```

Open http://127.0.0.1:5173/auth.html#/login. The development worker/Beat entry
point is `auth_app:celery`; inside the submission folder it is `app:celery`.
Redis runs on port 6379. Mailpit receives SMTP on 1025 and displays email on 8025.

## Optional demo data

After initialization, run `backend/venv/bin/python backend/seed_demo.py` to add
fictional accounts and representative scenarios. Read
[the demo data guide](backend/DEMO_DATA.md) for the public demo credentials,
fixed dates and repeat-run behavior. Existing Admin credentials are preserved.
Do not execute this against an unrelated production database.

## Milestones

The eight `backend/MILESTONE_*.md` files document the incremental commits.
For final setup use the submission README; earlier milestone commands reflect
what was available at that stage. Payments/refunds are simulated.
