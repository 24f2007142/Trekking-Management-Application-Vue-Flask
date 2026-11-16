# Milestone 3: Admin dashboard and management

Continue using the Milestone 2 entry points: `backend/auth_app.py` and
`frontend/auth.html`. The Admin placeholders are now replaced by the Admin
blueprint and full Admin screens. No new dependencies are required.

## Included

- Dashboard totals for treks, trekkers, staff and bookings.
- Create, edit, approve and remove treks; assign and cancel staff assignments.
- Create/edit staff, inspect assignment history and blacklist/reactivate staff.
- Search treks, staff and trekkers by name or ID.
- Inspect trekker profiles/history and blacklist/reactivate accounts.
- View all booking records and status-count reports.
- Update the Admin display name and log out.

Treks with bookings are cancelled instead of deleted to preserve records.
Completed treks with bookings are protected from deletion. Trekker profiles are
read-only to Admin; account status is managed separately. Staff/user operational
screens will be connected in their later milestones.

Admin APIs query SQLite directly in this milestone. Redis integration is deferred
to Milestone 8. A local reference copy of the original caching hooks is preserved
at `backend/instance/milestone-backups/admin-with-cache.py` (ignored by Git).
Reapply the hooks to the current routes at Milestone 8; do not blindly overwrite
later fixes with that backup. The untracked full `app.py` also uses these Admin
routes, so its Admin endpoints now bypass caching until that integration returns.

## Run and check

From the project root:

```bash
backend/venv/bin/python backend/init_db.py
backend/venv/bin/python backend/auth_app.py
```

In another terminal:

```bash
cd frontend
npx vite --config vite.auth.config.js --host 127.0.0.1
```

Open http://127.0.0.1:5173/auth.html#/login and log in as Admin. Check each sidebar
page, create a trek and staff account, assign that staff member, search both by
name/ID, and check blacklist/reactivate. Booking/history screens can be empty
until the booking milestone supplies records. Existing records are displayed.
Browser interaction has not been automated for this milestone.

Run the relevant automated checks:

```bash
cd backend
venv/bin/python -m unittest discover -s tests -p 'test_auth.py'
venv/bin/python -m unittest discover -s tests -p 'test_admin_users.py'
cd ../frontend
npx vite build --config vite.auth.config.js
```

## Commit

From the project root, stage exactly these 13 files:

```bash
git add backend/auth_app.py backend/routes/admin.py backend/tests/test_admin_users.py backend/MILESTONE_3.md frontend/src/router/auth.js frontend/src/layouts/AdminLayout.vue frontend/src/views/admin/AdminDashboard.vue frontend/src/views/admin/AdminTreks.vue frontend/src/views/admin/AdminStaff.vue frontend/src/views/admin/AdminUsers.vue frontend/src/views/admin/AdminBookings.vue frontend/src/views/admin/AdminReports.vue frontend/src/views/admin/AdminSettings.vue
git diff --cached --check
git diff --cached --stat
git diff --cached
git commit -m "Milestone-3: implement admin trek staff and user management"
git push origin main
```

Do not use `git add .`. If the remote has advanced and rejects your push,
reconcile those changes without force-pushing. Root README changes and other
untracked files remain outside this milestone.
