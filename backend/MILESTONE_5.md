# Milestone 5: User dashboard and trek bookings

Continue using `backend/auth_app.py` and `frontend/auth.html`. No new dependencies
or test files are added.

## Features

- Trekker dashboard, available treks, bookings, completed history and profile.
- Filter treks by name, location, difficulty and duration.
- Book available places and cancel upcoming bookings.
- Reject duplicate active bookings and bookings for full or closed treks.
- Restrict booking records/history to the logged-in user.
- Keep confirmed bookings visible with trek status and simulated payment status.

`confirmed` means Booked. Open booking requires an `upcoming` trek with
`bookings_open` enabled. Completed history is included because Milestone 5 asks
for it; Milestone 6 will review the complete cross-role lifecycle.

CSV export is deferred to Milestone 7 and Redis caching to Milestone 8. Reference
copies are kept locally in the ignored `backend/instance/milestone-backups/`
folder (`user-with-cache-and-export.py` and `UserHistory-with-export.vue`). Reapply
those features to current code later instead of overwriting newer fixes. The
untracked full app also imports these user routes, so its export endpoint and
user caching are temporarily absent.

## Run

From the project root:

```bash
backend/venv/bin/python backend/auth_app.py
```

In another terminal:

```bash
cd frontend
npx vite --config vite.auth.config.js --host 127.0.0.1
```

Open http://127.0.0.1:5173/auth.html#/login.

1. As Admin, create and approve a trek, assign staff and open bookings.
2. Register/log in as a trekker, filter treks and book a place.
3. Check My Bookings, cancel an upcoming booking and update My Profile.
4. Book again; as assigned staff, complete the trek. Verify it appears in the
   trekker's history.
5. Log in as another trekker and confirm their bookings/history stay separate.

Local checks passed for authentication/CSRF, profile updates, booking,
duplicate/full/closed rejection, cancellation, role access and private history
using a temporary database. The frontend production build passed. No check files
were added. Browser interaction still needs a manual check.

## Commit

From the project root, stage these 10 files:

```bash
git add backend/auth_app.py backend/routes/user.py backend/MILESTONE_5.md frontend/src/router/auth.js frontend/src/layouts/UserLayout.vue frontend/src/views/user/UserDashboard.vue frontend/src/views/user/UserTreks.vue frontend/src/views/user/UserBookings.vue frontend/src/views/user/UserHistory.vue frontend/src/views/user/UserSettings.vue
git diff --cached --check
git diff --cached --stat
git diff --cached
git commit -m "Milestone-5: implement user dashboard and trek booking system"
git push origin main
```

Do not use `git add .`. Leave tests, root README changes and other later-milestone
files unstaged. If the remote rejects the push, reconcile changes without
force-pushing.
