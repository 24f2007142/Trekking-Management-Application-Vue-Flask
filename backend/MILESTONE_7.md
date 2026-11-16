# Milestone 7: Background reminders, reports and CSV export

The existing `auth_app.py` now exposes a Celery app named `celery`. Keep using
`frontend/auth.html`. No test files are added.

## Jobs

- Daily at 08:00 Asia/Kolkata: email approved trekkers with confirmed bookings
  for upcoming treks starting tomorrow.
- Monthly on day 1 at 09:00 Asia/Kolkata: email approved Admin accounts an HTML
  report for the previous calendar month, including completed treks, participant
  places and the top five treks by participation.
- On the user's request: queue a CSV export and email it as an attachment when
  complete. It includes that user's completed/cancelled history, matching the
  history screen, with booking, trek and payment statuses.

The export API returns HTTP 202 and a task ID. The completion email is the user
notification; it is not a browser download. Redis uses database 0 for queued tasks
and database 1 for results. API caching remains for Milestone 8.

## Setup and run

Install backend dependencies from the project root:

```bash
backend/venv/bin/python -m pip install -r backend/requirements-milestone7.txt
```

Run Redis locally on port 6379. If an instance already runs, use it rather than
starting another. Otherwise, in a separate terminal:

```bash
redis-server
```

Email uses a local SMTP capture server at `127.0.0.1:1025`, without authentication.
Start your SMTP capture service on that address before running jobs. For example,
if Mailpit is installed, run `mailpit` and view captured messages at
http://127.0.0.1:8025. No capture service was found installed during preparation;
install/start one before the live email check. This configuration is for local
capture, not delivery to real email inboxes.

Run each of these in its own terminal from the project root:

```bash
backend/venv/bin/python backend/auth_app.py
```

```bash
cd backend
venv/bin/celery -A auth_app:celery worker --loglevel=info --pool=solo
```

```bash
cd backend
venv/bin/celery -A auth_app:celery beat --loglevel=info
```

```bash
cd frontend
npx vite --config vite.auth.config.js --host 127.0.0.1
```

Use only one Beat instance to avoid duplicate scheduled jobs. Workers and Beat
must use `auth_app:celery`, not the untracked full `app.py`. Restart the worker
after changing task code. Beat's local schedule files stay ignored by Git.

## Verify locally

Open http://127.0.0.1:5173/auth.html#/login. Log in as a trekker, open Trekking
History and click Export history as CSV. The page confirms the request; inspect
the local SMTP capture inbox for the completion email and CSV attachment.

To exercise scheduled jobs immediately, with the worker and mail capture running,
run these from `backend` (they enqueue jobs and produce local emails):

```bash
venv/bin/celery -A auth_app:celery call tasks.send_daily_reminders
venv/bin/celery -A auth_app:celery call tasks.send_monthly_report
```

Reminder data must include a confirmed booking on an upcoming trek starting
tomorrow. Reports count completed treks ending in the previous month; an empty
month still produces a report. SMTP/worker errors appear in the worker terminal.
If Redis is unavailable, the export endpoint returns a service-unavailable error.
An accepted task still needs a running worker and SMTP server to finish.

Preparation checks passed with a real Celery worker using an in-memory broker,
a temporary database and captured SMTP calls: reminders, monthly HTML, async
export authorization, private CSV rows and attachments. The frontend build also
passed. Live Redis, Beat timing, SMTP delivery and browser interaction remain
manual checks. No external emails were sent during preparation.

## Commit

From the project root, stage these nine files:

```bash
git add backend/auth_app.py backend/routes/user.py backend/celery_setup.py backend/tasks.py backend/email_utils.py backend/templates/monthly_report.html backend/requirements-milestone7.txt backend/MILESTONE_7.md frontend/src/views/user/UserHistory.vue
git diff --cached --check
git diff --cached --stat
git diff --cached
git commit -m "Milestone-7: add scheduled trek reminders reports and CSV exports"
git push origin main
```

Do not use `git add .`. Leave tests, root README changes, cache.py and other
later-milestone files unstaged. Reconcile a rejected push without force-pushing.
