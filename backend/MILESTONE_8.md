# Milestone 8: Redis API caching

Continue using `backend/auth_app.py` and `frontend/auth.html`. The Redis package
is already included in `requirements-milestone7.txt`; no new dependency or test
file is needed.

## Cached endpoints

- `GET /api/user/treks`: a separate entry per user because booking flags differ.
- `GET /api/user/treks/<id>`: a separate entry per trek.
- `GET /api/admin/treks`: a separate entry per normalized search term.

All role and account checks run before reading cached data. Booking writes still
check SQLite, so stale listing data cannot bypass the booking capacity checks.
History and CSV exports retain the changes from Milestones 6 and 7.

## How it works

1. Read the response from Redis if present.
2. Otherwise, query SQLite and save the response to Redis.
3. Each entry expires 300 seconds after it is saved. Reading does not extend it.
4. After a successful relevant database change, clear the trek cache. The next
   request reloads fresh data from SQLite.

Invalidation follows Admin trek creation/edit/approval/deletion and user
blacklisting; staff capacity, booking availability, lifecycle and participant
changes; and user booking/cancellation. All variants are cleared together so
other users also see updated availability.

Cache entries use Redis database 2 and the prefix `hi-trek:treks:`. Celery uses
databases 0 and 1. Invalidation deletes only keys with that prefix, never all Redis
data. If Redis fails, requests fall back to SQLite. Failed invalidation can leave
old entries until their original expiry. This simple policy does not guarantee
instant consistency during simultaneous reads/writes.

## Run and inspect

Use the Redis server already running for Celery. If none runs, start one with
`redis-server` in its own terminal. No separate cache worker is needed.

From the project root:

```bash
backend/venv/bin/python backend/auth_app.py
```

In another terminal:

```bash
cd frontend
npx vite --config vite.auth.config.js --host 127.0.0.1
```

Open http://127.0.0.1:5173/auth.html#/login. Log in as a trekker and open Available
Treks, or log in as Admin and open Treks. Inspect the generated keys:

```bash
redis-cli -n 2 --scan --pattern 'hi-trek:treks:*'
```

Copy an actual key from that output into the TTL command, for example:

```bash
redis-cli -n 2 TTL 'hi-trek:treks:user:2:listing'
```

Replace `2` in the key with the actual user ID. A positive TTL is seconds until
expiry; `-2` means that key is absent. After a booking or trek edit, old entries
are cleared; page refreshes may immediately create fresh entries.

## Verification

Eight existing local cache checks passed, covering cache hits skipping trek
queries, expiry, user separation, authorization, invalidation after writes and
Redis-outage fallback. No check files were added or included in this commit.
A separate temporary real Redis instance also verified reads/writes, the
300-second TTL, expiry and prefix-only deletion. That check did not touch the
application database or the user's running Redis data. No latency benchmark was
performed; the demonstrated optimization is avoiding repeated trek queries.

## Commit

From the project root, stage these five files:

```bash
git add backend/cache.py backend/routes/admin.py backend/routes/staff.py backend/routes/user.py backend/MILESTONE_8.md
git diff --cached --check
git diff --cached --stat
git diff --cached
git commit -m "Milestone-8: cache trek APIs with Redis expiry and invalidation"
git push origin main
```

Do not use `git add .`. Leave tests, root README changes and untracked landing-page
or full-app files unstaged. If the push is rejected because the remote advanced,
reconcile changes without force-pushing.
