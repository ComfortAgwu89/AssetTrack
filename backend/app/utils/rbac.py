"""Role-based access control: permission catalogue, role map and route decorator."""
from functools import wraps

from flask import g, jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.extensions import db

PERMISSIONS = {
    "dashboard.view": "View the dashboard",
    "dashboard.activity": "See organisation-wide recent activity",
    "asset.view": "View assets",
    "asset.create": "Register assets",
    "asset.edit": "Edit assets",
    "asset.archive": "Archive assets",
    "category.manage": "Manage asset categories",
    "department.manage": "Manage departments",
    "custodian.manage": "Manage custodians",
    "assignment.manage": "Assign assets to custodians",
    "transfer.request": "Request transfers",
    "transfer.approve": "Approve or reject transfers",
    "transfer.confirm": "Confirm approved transfers",
    "depreciation.view": "View depreciation",
    "depreciation.manage": "Post and configure depreciation",
    "maintenance.report": "Report faulty assets",
    "maintenance.manage": "Manage maintenance",
    "verification.perform": "Perform physical verification",
    "verification.manage": "Create verification lists",
    "disposal.manage": "Record asset disposals",
    "disposal.approve": "Approve disposals",
    "report.view": "View and export reports",
    "audit.view": "View the audit trail",
    "user.manage": "Manage users and roles",
    "settings.manage": "Manage organisation settings",
    "platform.manage": "Manage the whole platform",
}

_ALL = set(PERMISSIONS)

ROLES = {
    "super_admin": {
        "name": "Super Administrator",
        "description": "Manages the entire platform.",
        "permissions": _ALL,
    },
    "org_admin": {
        "name": "Organisation Administrator",
        "description": "Manages organisational records and users.",
        "permissions": _ALL - {"platform.manage"},
    },
    "accountant": {
        "name": "Accountant",
        "description": "Manages asset values, depreciation and reports.",
        "permissions": {
            "dashboard.view", "dashboard.activity", "asset.view", "depreciation.view",
            "depreciation.manage", "disposal.manage", "disposal.approve", "report.view", "audit.view",
        },
    },
    "asset_manager": {
        "name": "Asset Manager",
        "description": "Registers assets, assigns custodians and manages transfers.",
        "permissions": {
            "dashboard.view", "dashboard.activity", "asset.view", "asset.create", "asset.edit",
            "asset.archive", "category.manage", "custodian.manage", "assignment.manage",
            "transfer.request", "transfer.confirm", "maintenance.manage", "maintenance.report",
            "verification.manage", "verification.perform", "disposal.manage", "report.view",
        },
    },
    "department_head": {
        "name": "Department Head",
        "description": "Views department assets and approves relevant requests.",
        "permissions": {
            "dashboard.view", "asset.view", "transfer.request", "transfer.approve",
            "maintenance.report", "report.view",
        },
    },
    "asset_custodian": {
        "name": "Asset Custodian",
        "description": "Views assigned assets and reports their condition.",
        "permissions": {"dashboard.view", "asset.view", "maintenance.report", "verification.perform"},
    },
}


def error_response(message, status, details=None):
    body = {"message": message}
    if details:
        body["details"] = details
    return jsonify(error=body), status


def current_user():
    from app.models import User

    identity = get_jwt_identity()
    return db.session.get(User, int(identity)) if identity is not None else None


def require_permission(*codes):
    """Require a valid session and, if codes are given, at least one of them."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user = current_user()
            if user is None or not user.is_active or not user.organisation.is_active:
                return error_response("Account is not active.", 401)
            if codes and not any(user.has_permission(c) for c in codes):
                return error_response("You do not have permission to perform this action.", 403)
            g.current_user = user
            return fn(*args, **kwargs)

        return wrapper

    return decorator
