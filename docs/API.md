# AssetTrack API (Stage 1)

Base path: `/api`. All bodies are JSON. Authentication is an httpOnly cookie set by login/register; state-changing requests must send the CSRF token from the `csrf_access_token` cookie in an `X-CSRF-TOKEN` header (the frontend does this automatically).

Errors use one shape:

```json
{ "error": { "message": "Human readable message", "details": { "field": "problem" } } }
```

| Status | Meaning |
| --- | --- |
| 400 | Bad request parameter |
| 401 | Not signed in / session expired |
| 403 | Signed in but lacking the required permission |
| 404 | Not found (also returned for records in another organisation) |
| 422 | Validation failed; `details` lists fields |

## Endpoints

| Method | Path | Permission | Description |
| --- | --- | --- | --- |
| GET | `/health` | none | Liveness check |
| POST | `/auth/register` | none | Create an organisation and its Organisation Administrator. Body: `organisation_name`, `full_name`, `email`, `password` (8+ chars, letters and numbers). Returns `201` and `{ user }`. |
| POST | `/auth/login` | none | Body: `email`, `password`. Returns `{ user }` and sets the session cookie. |
| POST | `/auth/logout` | none | Clears the session cookie. |
| GET | `/auth/me` | signed in | Current user, role and permission list. |
| GET | `/dashboard` | `dashboard.view` | Dashboard figures. Optional query: `department_id`, `category_id`. |
| GET | `/roles` | `user.manage` | Roles and their permissions (super administrator role hidden from non-super admins). |

## `GET /dashboard` response

```json
{
  "as_of": "2026-11-20",
  "kpis": {
    "total_assets": 27, "total_acquisition_cost": 0.0, "accumulated_depreciation": 0.0,
    "net_book_value": 0.0, "assets_in_use": 0, "under_maintenance": 0,
    "damaged": 0, "missing": 0, "fully_depreciated": 0
  },
  "by_department": [{ "label": "Computer Science", "value": 6 }],
  "by_category": [{ "label": "Computer Equipment", "value": 6 }],
  "by_status": [{ "label": "in_use", "value": 20 }],
  "depreciation_by_category": [{ "category": "Vehicles", "cost": 0.0, "accumulated": 0.0, "nbv": 0.0 }],
  "recent_activity": [{ "id": 1, "action": "asset.create", "summary": "...", "user": "...", "created_at": "..." }],
  "filters": { "departments": [{ "id": 1, "name": "..." }], "categories": [{ "id": 1, "name": "..." }] },
  "scope": "org_admin"
}
```

How figures are defined:

- The **register** is all non-archived, non-disposed assets in the caller's visible scope. Totals, net book value and every breakdown use this same set, so they reconcile (`cost - accumulated = net book value`; breakdown counts sum to `total_assets`).
- **Net book value** is computed at request time from each asset's depreciation settings using `app/services/depreciation.py`.
- `damaged` counts assets whose condition is *damaged*; `missing` counts assets whose status is *missing*.
- `recent_activity` is returned only to roles with `dashboard.activity`.
- Scope: department heads see their department; custodians see assets assigned to them.

## Permission catalogue

Defined in `backend/app/utils/rbac.py` (`PERMISSIONS` and `ROLES`).
