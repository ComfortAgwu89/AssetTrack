from flask import Blueprint, g, jsonify

from app.models import Role
from app.utils.rbac import require_permission

bp = Blueprint("roles", __name__)


@bp.get("/roles")
@require_permission("user.manage")
def list_roles():
    roles = Role.query.order_by(Role.id).all()
    if g.current_user.role.key != "super_admin":
        roles = [r for r in roles if r.key != "super_admin"]
    return jsonify(
        roles=[
            {"key": r.key, "name": r.name, "description": r.description, "permissions": sorted(r.permission_codes)}
            for r in roles
        ]
    )
