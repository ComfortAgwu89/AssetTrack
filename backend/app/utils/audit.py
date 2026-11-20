from flask import request

from app.extensions import db
from app.models import AuditLog


def log_action(action, organisation_id, user=None, entity_type=None, entity_id=None, summary=None, changes=None):
    """Append an audit entry to the current session. The caller commits."""
    entry = AuditLog(
        organisation_id=organisation_id,
        user_id=user.id if user else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        summary=summary,
        changes=changes,
        ip_address=request.remote_addr if request else None,
    )
    db.session.add(entry)
    return entry


def diff(old: dict, new: dict):
    """Return {field: {old, new}} for fields whose values differ."""
    return {k: {"old": old.get(k), "new": v} for k, v in new.items() if old.get(k) != v}
