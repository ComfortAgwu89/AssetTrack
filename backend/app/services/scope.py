"""Visibility rules: every asset query goes through here for isolation and role scope."""
from app.models import Asset, Custodian


def scoped_assets(user):
    """Assets this user may see.

    * Always limited to the user's own organisation (data isolation).
    * Department heads see only their department's assets.
    * Custodians see only assets assigned to them.
    """
    query = Asset.query.filter(Asset.organisation_id == user.organisation_id)
    role = user.role.key
    if role == "department_head":
        if user.department_id is None:
            return query.filter(Asset.id == -1)
        query = query.filter(Asset.department_id == user.department_id)
    elif role == "asset_custodian":
        ids = [c.id for c in Custodian.query.filter_by(user_id=user.id, organisation_id=user.organisation_id)]
        query = query.filter(Asset.custodian_id.in_(ids)) if ids else query.filter(Asset.id == -1)
    return query
