# Milestone 6: Booking history and trek status tracking

This milestone builds on the lifecycle already introduced in Milestones 3–5.
It uses the same `auth_app.py` and `auth.html` entry points and adds no dependencies,
schema changes or test files.

## Changes

- Trekking History includes cancelled bookings as well as completed treks, with
  booking dates, trek dates, booking status and payment status.
- User bookings/history display `confirmed` as Booked and `upcoming` as Open or
  Closed according to the booking switch. Database values stay unchanged.
- Completed and cancelled trek details are read-only to Admin to preserve history.
- Completed treks cannot be deleted, even when no bookings exist.
- Admin Edit/Delete controls reflect these restrictions.

## Status mapping

| Requirement | Stored representation |
| --- | --- |
| Pending | trek_status = pending |
| Approved | trek_status = approved |
| Open | trek_status = upcoming and bookings_open = true |
| Closed before starting | trek_status = upcoming and bookings_open = false |
| Started / ongoing | trek_status = ongoing; bookings closed |
| Completed | trek_status = completed; confirmed bookings become completed |
| Booked | booking status = confirmed |
| Cancelled | booking status = cancelled; record retained |

Admin approves a pending trek. Admin or assigned staff opens bookings after
approval. Assigned staff starts/completes it. Completed/cancelled treks cannot
reopen. A cancelled booking can be rebooked as a new record while the trek is open.

User history is restricted to the signed-in user. Admin can inspect all bookings
and individual user history. Assigned/completed staff assignments retain access
to participant records; cancelled assignments cannot access participant records.
Deletion of a trek with bookings cancels it while retaining its records, except
that completed treks are always protected. Payments/refunds are simulated.

## Verification

Local checks against a temporary database passed for approval/open/start/complete,
concurrent capacity limits, duplicate bookings, cancellation/rebooking history,
completed-record protection and role-restricted records. The frontend build
passed. The application database was not modified. Browser checks remain manual.

Run the backend and frontend as before:

```bash
# Project root
backend/venv/bin/python backend/auth_app.py
```

```bash
# Separate terminal, from the project root
cd frontend
npx vite --config vite.auth.config.js --host 127.0.0.1
```

Open http://127.0.0.1:5173/auth.html#/login. Create a disposable trek as Admin,
approve it, assign staff and open bookings. As trekker, book, cancel and check
history, then rebook. As assigned staff, mark it ongoing and completed. Verify
both booking records remain in user history and Admin/staff records. Confirm
Admin cannot edit/delete the completed trek and staff cannot reopen it.

## Commit

From the project root, stage these six files:

```bash
git add backend/routes/admin.py backend/routes/user.py backend/MILESTONE_6.md frontend/src/views/admin/AdminTreks.vue frontend/src/views/user/UserBookings.vue frontend/src/views/user/UserHistory.vue
git diff --cached --check
git diff --cached --stat
git diff --cached
git commit -m "Milestone-6: preserve booking history and protect completed trek records"
git push origin main
```

Leave test changes and other later-milestone files unstaged. Do not use
`git add .` or force-push if the remote rejects your push.
