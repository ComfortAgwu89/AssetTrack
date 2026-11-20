from collections import defaultdict
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import joinedload

from app.models import Asset, AssetCategory, AuditLog, Department
from app.services.depreciation import compute_position
from app.services.scope import scoped_assets

ZERO = Decimal("0.00")


def money(value):
    return float(Decimal(value).quantize(Decimal("0.01")))


def build_dashboard(user, department_id=None, category_id=None, as_of=None):
    """All figures are computed from asset records at request time.

    "Register" = non-archived, non-disposed assets. Totals, net book value and the
    chart breakdowns all use this same set, so they reconcile with each other.
    """
    as_of = as_of or date.today()
    query = scoped_assets(user).filter(Asset.is_archived.is_(False))
    if department_id:
        query = query.filter(Asset.department_id == department_id)
    if category_id:
        query = query.filter(Asset.category_id == category_id)
    assets = query.options(joinedload(Asset.category), joinedload(Asset.department)).all()

    register = [a for a in assets if a.status != "disposed"]
    total_cost = total_accum = ZERO
    fully = 0
    by_department = defaultdict(int)
    by_category = defaultdict(int)
    by_status = defaultdict(int)
    dep_by_category = defaultdict(lambda: {"cost": ZERO, "accumulated": ZERO, "nbv": ZERO})

    for a in register:
        pos = compute_position(a.depreciation_params(), as_of)
        total_cost += a.acquisition_cost
        total_accum += pos.accumulated
        fully += 1 if pos.fully_depreciated else 0
        by_department[a.department.name if a.department else "Unassigned"] += 1
        by_category[a.category.name] += 1
        by_status[a.status] += 1
        row = dep_by_category[a.category.name]
        row["cost"] += a.acquisition_cost
        row["accumulated"] += pos.accumulated
        row["nbv"] += pos.carrying_amount

    kpis = {
        "total_assets": len(register),
        "total_acquisition_cost": money(total_cost),
        "accumulated_depreciation": money(total_accum),
        "net_book_value": money(total_cost - total_accum),
        "assets_in_use": sum(1 for a in register if a.status == "in_use"),
        "under_maintenance": sum(1 for a in register if a.status == "under_maintenance"),
        "damaged": sum(1 for a in register if a.condition == "damaged"),
        "missing": sum(1 for a in register if a.status == "missing"),
        "fully_depreciated": fully,
    }

    activity = []
    if user.has_permission("dashboard.activity"):
        logs = (
            AuditLog.query.filter_by(organisation_id=user.organisation_id)
            .order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
            .limit(10)
            .all()
        )
        activity = [
            {
                "id": log.id,
                "action": log.action,
                "summary": log.summary,
                "user": log.user.full_name if log.user else "System",
                "created_at": log.created_at.isoformat() if log.created_at else None,
            }
            for log in logs
        ]

    org_id = user.organisation_id
    filters = {
        "departments": [
            {"id": d.id, "name": d.name}
            for d in Department.query.filter_by(organisation_id=org_id, is_active=True).order_by(Department.name)
        ],
        "categories": [
            {"id": c.id, "name": c.name}
            for c in AssetCategory.query.filter_by(organisation_id=org_id, is_active=True).order_by(AssetCategory.name)
        ],
    }

    return {
        "as_of": as_of.isoformat(),
        "kpis": kpis,
        "by_department": _series(by_department),
        "by_category": _series(by_category),
        "by_status": _series(by_status),
        "depreciation_by_category": [
            {"category": name, **{k: money(v) for k, v in row.items()}}
            for name, row in sorted(dep_by_category.items())
        ],
        "recent_activity": activity,
        "filters": filters,
        "scope": user.role.key,
    }


def _series(mapping):
    return [{"label": k, "value": v} for k, v in sorted(mapping.items(), key=lambda kv: (-kv[1], kv[0]))]
