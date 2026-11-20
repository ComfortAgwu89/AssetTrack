from datetime import date

from app.models import Asset


def next_asset_tag(organisation, category, acquisition_date=None):
    """Generate a unique tag like HVU-COMP-2024-0007 (sequence is per organisation and year)."""
    year = (acquisition_date or date.today()).year
    prefix = f"{organisation.asset_prefix}-{category.code}-{year}-"
    existing = Asset.query.filter(
        Asset.organisation_id == organisation.id, Asset.asset_tag.like(prefix + "%")
    ).count()
    return f"{prefix}{existing + 1:04d}"
