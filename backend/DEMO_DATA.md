# Optional demonstration data

`seed_demo.py` contains fictional data definitions, not a copy of the application
database. It adds **10 trekkers, 10 staff and 10 treks**, plus 16 bookings and nine
staff assignments. Admin is separate and is not counted among these 20 accounts.

Run `init_db.py` first. From this backend folder:

```bash
venv/bin/python seed_demo.py
```

All demo accounts use password **DemoTrek2026!**. Trekker emails are
`trekker01@demo.example.test` through `trekker10@demo.example.test`; staff emails
are `staff01@demo.example.test` through `staff10@demo.example.test`.
These are deliberately public local-demo credentials, not real users or secrets.
The script never changes the Admin password.

For each role, accounts 01–08 are approved, 09 is pending, and 10 is blacklisted.
Accounts 09/10 cannot log in. Trekker 08 has no bookings; staff 08 has no assignment.
Contact numbers are obvious dummy values. No messages are sent by the seed script.

| Trek | Dates in 2026 | Scenario |
| --- | --- | --- |
| Open Easy Walk | Dec 10 | Open, 3/10 places booked; one cancelled booking |
| Open Mountain Trail | Dec 12–13 | Open, 2/8 booked; one staff removal/refund initiated |
| Full Summit Trek | Dec 15–17 | Open but full, 3/3 places booked |
| Closed Forest Trail | Dec 19–20 | Closed with an existing booking |
| Awaiting Approval | Dec 22 | Pending approval, unassigned, cannot be booked |
| Approved Ridge Trek | Dec 24–25 | Approved and assigned; bookings not yet opened |
| In Progress Valley | Nov 18–20 | Ongoing, bookings closed |
| Completed Lake Walk | Oct 10 | Completed with 3 participant places |
| Completed Peak Trek | Oct 20–21 | Completed with 4 participant places |
| Cancelled Coastal Walk | Dec 28 | Cancelled trek, refunded bookings, cancelled assignment |

Trek names start with `[Demo]`. All upcoming treks start on or after December 10,
2026. The two October treks produce a November monthly report with two treks and
seven participant places. Dates are fixed for this demonstration, not automatically
moved forward. For a later month's report, create appropriate completed data.
The reminder job will select the December 10 booking on December 9; before then
these seeds intentionally do not provide a tomorrow-reminder case.

There are no pending bookings because the current booking flow immediately
confirms successful bookings. This data covers the main supported scenarios,
not every possible combination of account and trek statuses.

Existing records are preserved, so a nonempty database may contain more than
10 users/staff/treks in total. A backup is created next to the database before the
first seed. Re-running preserves existing demo records and any changes made during
a demonstration. If only some matching demo names already exist, the script stops
without writing instead of guessing how to merge them. Use a fresh initialized
database if you need the exact original demonstration state.

The script supports `--database /path/to/users.db` for a separate initialized
SQLite database. Do not submit databases or backups. If the app was already open,
allow up to five minutes for the existing Redis cache to expire.
