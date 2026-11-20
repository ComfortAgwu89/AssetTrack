from flask import Blueprint, g, jsonify, request

from app.models import AssetCategory, Department
from app.services.dashboard import build_dashboard
from app.utils.rbac import error_response, require_permission

bp = Blueprint("dashboard", __name__)


def _int_arg(name):
    raw = request.args.get(name)
    if raw in (None, ""):
        return None
    try:
        return int(raw)
    except ValueError:
        raise ValueError(f"{name} must be a whole number.")


@bp.get("/dashboard")
@require_permission("dashboard.view")
def dashboard():
    user = g.current_user
    try:
        department_id = _int_arg("department_id")
        category_id = _int_arg("category_id")
    except ValueError as exc:
        return error_response(str(exc), 400)

    # Filters must belong to the caller's organisation (isolation).
    if department_id and not Department.query.filter_by(id=department_id, organisation_id=user.organisation_id).first():
        return error_response("Department not found.", 404)
    if category_id and not AssetCategory.query.filter_by(id=category_id, organisation_id=user.organisation_id).first():
        return error_response("Category not found.", 404)

    return jsonify(build_dashboard(user, department_id=department_id, category_id=category_id))
