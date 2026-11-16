# Milestone 2: Authentication and role access

This commit uses `backend/auth_app.py` and `frontend/auth.html` as independent
entry points. The existing untracked `app.py`, main Vue router, and management
screens remain intact for later milestones. Do not stage those files yet.

## Run

From the project root:

```bash
backend/venv/bin/python -m pip install -r backend/requirements-milestone2.txt
backend/venv/bin/python backend/init_db.py
backend/venv/bin/python backend/auth_app.py
```

In another terminal:

```bash
cd frontend
npm ci
npx vite --config vite.auth.config.js --host 127.0.0.1
```

Open http://127.0.0.1:5173/auth.html#/login. Use this host consistently for cookie
authentication. Log in with the Admin credentials from Milestone 1. Admin can
create a staff account on the simple Admin dashboard. Log out, then test staff
login. Register a trekker through the registration screen and test trekker login.
Public registration always creates a trekker, regardless of a supplied role.

Each role is redirected to its own dashboard. Both the Vue router and backend
protect role access. Account status is checked on every protected request.
JWTs use HTTP-only cookies; the readable CSRF cookie is sent in a header for staff
creation. Passwords are hashed. Admin is created only by init_db.py.

A random signing secret is generated on startup, so restarting the backend logs
users out. Set the SECRET_KEY environment variable to a private persistent value
if stable sessions across restarts are needed. Do not commit that value.

## Verify

```bash
cd backend
venv/bin/python -m unittest discover -s tests -p 'test_auth.py'
cd ../frontend
npx vite build --config vite.auth.config.js
```

Also verify the three login redirects and logout in the browser. The backend
tests cover cookies, CSRF, role isolation, staff creation, registration privilege
protection, invalid passwords and blacklisted accounts.

## Stage and commit

Run from the project root:

```bash
git add backend/auth_app.py backend/requirements-milestone2.txt backend/MILESTONE_2.md backend/tests/test_auth.py frontend/package.json frontend/package-lock.json frontend/auth.html frontend/vite.auth.config.js frontend/src/App.vue frontend/src/main-auth.js frontend/src/router/auth.js frontend/src/components/LoginView.vue frontend/src/components/RegisterView.vue frontend/src/components/AuthDashboard.vue
git diff --cached --check
git diff --cached --stat
git diff --cached
git commit -m "Milestone-2: add JWT authentication and role-based dashboard access"
git push origin main
```

Expect 14 staged files, all listed above. Do not use `git add .`. If the push is
rejected because the remote changed, reconcile it without force-pushing.

For later milestones, integrate these authentication and role-access improvements
into the full app entry points as their dependencies are committed. Keep one
canonical authentication implementation once the full app is included.
