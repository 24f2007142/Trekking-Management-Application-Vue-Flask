# Milestone 4: Staff dashboard and trek operations

Continue using `backend/auth_app.py` and `frontend/auth.html`. The staff
placeholder now uses the Staff blueprint, layout and operational screens.
No new dependencies are needed.

## Included

- Staff dashboard with assigned treks and participant-place counts.
- Assigned trek details, slot changes and Open/Closed booking controls.
- Start a trek (`ongoing`) and mark it completed.
- View/search participants and remove confirmed participants.
- Staff profile updates and logout.
- Server-side role, account-status and assignment checks.

Cancelled assignment rows remain visible as assignment history; their details,
participant records and management actions are blocked. Completed assignments
retain read access to participant history. Capacity cannot be reduced below
booked places, and completed treks cannot be reopened. Removing a participant
preserves their booking as cancelled, releases slots and records the staff name.
Refund status is simulated; no payment transfer occurs.

The dashboard counts reserved participant places, which may exceed the number of
booking accounts when one booking reserves multiple places. Booking creation
arrives in Milestone 5. Until then, participant screens can be empty on a fresh
database; tests use isolated booking fixtures to verify participant operations.

Redis invalidation is deferred to Milestone 8. The original staff routes are
preserved locally at `backend/instance/milestone-backups/staff-with-cache.py`,
which Git ignores. Reapply those hooks to the latest code at Milestone 8 rather
than restoring the old file over later fixes. The untracked full app also imports
these staff routes, so its staff mutations temporarily do not invalidate Redis.

## Run and manually verify

From the project root:

```bash
backend/venv/bin/python backend/auth_app.py
```

In another terminal:

```bash
cd frontend
npx vite --config vite.auth.config.js --host 127.0.0.1
```

Open http://127.0.0.1:5173/auth.html#/login. As Admin, create a staff account,
create and approve a trek, and assign that staff member. Log out and log in as
staff. Check Dashboard, My Treks, Participants and My Profile. Change capacity,
open/close bookings, start the trek and complete it. Use a disposable trek for
this check because completion cannot be reversed. Log in as another unassigned
staff member and verify the trek is not listed. Browser checks have not been
automated for this milestone.

## Automated checks

```bash
cd backend
venv/bin/python -m unittest discover -s tests -p 'test_staff_operations.py'
venv/bin/python -m unittest discover -s tests -p 'test_auth.py'
venv/bin/python -m unittest discover -s tests -p 'test_admin_users.py'
cd ../frontend
npx vite build --config vite.auth.config.js
```

The 20 backend tests cover staff assignment restrictions, CSRF, capacity bounds,
booking availability, lifecycle transitions, participant removal, authentication
and Admin regression checks. Tests do not alter the application database.

## Commit

From the project root, stage these 11 files:

```bash
git add backend/auth_app.py backend/routes/staff.py backend/tests/test_auth.py backend/tests/test_staff_operations.py backend/MILESTONE_4.md frontend/src/router/auth.js frontend/src/layouts/StaffLayout.vue frontend/src/views/staff/StaffDashboard.vue frontend/src/views/staff/ManageTreks.vue frontend/src/views/staff/ManageParticipants.vue frontend/src/views/staff/StaffSettings.vue
git diff --cached --check
git diff --cached --stat
git diff --cached
git commit -m "Milestone-4: implement assigned staff trek operations"
git push origin main
```

Do not use `git add .`. Keep root README changes and later-milestone files
unstaged. If a push is rejected because the remote changed, reconcile those
changes without force-pushing.
