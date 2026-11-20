# AssetTrack

**Fixed Asset Management and Accountability System** – a web application for tracking the full lifecycle of an organisation's physical assets.

- **Frontend:** Vue 3, Vite, Vue Router, Pinia, Tailwind CSS, Lucide icons, Chart.js
- **Backend:** Python Flask, SQLAlchemy, Flask-Migrate, Flask-JWT-Extended, PostgreSQL
- **Currency:** configurable per organisation, default Nigerian naira (₦)

> Depreciation figures and reports are management information, not audited financial statements.

## Status

| Stage | Scope | State |
| --- | --- | --- |
| 1 | Foundation: project structure, database models, authentication, role-based access, dashboard | **Written; needs your first local run** (see "Verification status") |
| 2 | Asset records: assets, categories, departments, custodians, assignments, user management | Not started |
| 3 | Lifecycle: transfers, depreciation posting, maintenance, verification, disposal | Not started |
| 4 | Reports (PDF/Excel), audit trail screens, notifications, settings | Not started |
| 5 | Security review, full demo data, deployment | Not started |

Sidebar items for later stages open a "not built yet" page that names the stage they belong to.

### Verification status

- ✅ Depreciation engine unit tests (19) pass: `backend/tests/test_depreciation.py`.
- ⚠️ The Flask API tests, the database models, the seed data and the entire Vue frontend were written in an environment without package installs, so **they have not been run yet**. Expect to fix small errors on first run and report them back.

## Prerequisites

- Python 3.11+
- Node.js 20+ and npm
- PostgreSQL 14+

## Database setup

```bash
# 1. Create a database user and database (choose your own password)
sudo -u postgres psql -c "CREATE USER assettrack_user WITH PASSWORD 'YOUR_DB_PASSWORD';"
sudo -u postgres psql -c "CREATE DATABASE assettrack OWNER assettrack_user;"
```

## Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp ../.env.example .env              # then edit .env: set DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY
```

Create the schema with migrations (the `migrations/` folder is generated on your machine the first time):

```bash
export FLASK_APP=run.py              # Windows PowerShell: $env:FLASK_APP="run.py"
flask db init
flask db migrate -m "initial schema"
flask db upgrade
```

Load roles and the fictional demo organisation, then start the API:

```bash
flask seed-demo
python run.py                        # API on http://127.0.0.1:5000
```

Commit the generated `migrations/` folder so the schema is versioned.

## Frontend setup

```bash
cd frontend
npm install
npm run dev                          # http://localhost:5173
```

Vite proxies `/api` to the Flask server, so run both at the same time.

## Demo accounts

Demo organisation: **Harbourview University** (fictional). All demo accounts use the password in `DEMO_PASSWORD` from your `.env`, or `Demo@12345` if it is not set. **Development only – never use demo accounts or this password in production.**

| Role | Email | What to look for |
| --- | --- | --- |
| Super Administrator | superadmin@harbourview.example | All permissions |
| Organisation Administrator | admin@harbourview.example | Everything except platform management; User Management |
| Accountant | accountant@harbourview.example | Depreciation, reports, audit |
| Asset Manager | manager@harbourview.example | Dashboard shows the whole organisation |
| Department Head | depthead@harbourview.example | Dashboard limited to Computer Science |
| Asset Custodian | custodian@harbourview.example | Dashboard limited to assets assigned to them |

## Testing

```bash
cd backend
pytest                       # everything
pytest tests/test_depreciation.py   # accounting calculations only (needs no database)
```

API tests use an in-memory SQLite database; no PostgreSQL is needed to run them.

## Key design decisions

- **Auth:** JWT in an httpOnly cookie with double-submit CSRF protection (`X-CSRF-TOKEN` header). The token is never readable by JavaScript.
- **Roles:** the six roles and their permissions are defined in `backend/app/utils/rbac.py`, stored in the `roles`/`permissions` tables by `flask seed-roles`, and enforced on every API route. The frontend hides menu items it cannot use, but the backend is the real gate.
- **Data isolation:** every query is filtered by the signed-in user's organisation; department heads and custodians are further limited to their own assets (`backend/app/services/scope.py`).
- **Depreciation:** pure functions in `backend/app/services/depreciation.py`, documented at the top of the file (whole-month pro-rating, floor at residual value, stops at end of life, frozen at disposal).
- **Audit trail:** append-only; the application raises an error on any update or delete of an audit entry. A database-level trigger will be added in Stage 5.
- **Assumptions:** the brief specifies React, but this project uses Vue 3 as requested. A user belongs to exactly one organisation, so super administrators are attached to an organisation for now.

## Project structure

```
backend/
  app/
    models/      database models (organisation/users, master data, assets & lifecycle, audit)
    routes/      REST endpoints (auth, dashboard, roles, health)
    services/    business logic (depreciation, dashboard, visibility scope)
    utils/       RBAC and audit helpers
    seed.py      roles/permissions and demo data (flask seed-roles / seed-demo)
  tests/         pytest suites
  config.py  run.py  requirements.txt
frontend/
  src/ components/ views/ layouts/ router/ stores/ services/ composables/ styles/
docs/API.md      API reference
```

## Deployment notes

Target: Render or AWS. Set `FLASK_ENV=production`, strong `SECRET_KEY`/`JWT_SECRET_KEY`, `DATABASE_URL`, and `JWT_COOKIE_SECURE=true`. Serve the built frontend (`npm run build`) and the API from the same origin, or configure CORS and cookie settings accordingly. Full deployment documentation is planned for Stage 5.
