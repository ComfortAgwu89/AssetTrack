from app.extensions import db
from app.models.base import TimestampMixin


class Department(TimestampMixin, db.Model):
    __tablename__ = "departments"
    __table_args__ = (db.UniqueConstraint("organisation_id", "code", name="uq_department_org_code"),)

    id = db.Column(db.Integer, primary_key=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey("organisations.id"), nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(12), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class Location(TimestampMixin, db.Model):
    __tablename__ = "locations"

    id = db.Column(db.Integer, primary_key=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey("organisations.id"), nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.String(300))
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class AssetCategory(TimestampMixin, db.Model):
    __tablename__ = "asset_categories"
    __table_args__ = (db.UniqueConstraint("organisation_id", "code", name="uq_category_org_code"),)

    id = db.Column(db.Integer, primary_key=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey("organisations.id"), nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(8), nullable=False)
    default_useful_life_years = db.Column(db.Numeric(5, 2), nullable=False, default=5)
    default_depreciation_method = db.Column(db.String(20), nullable=False, default="straight_line")
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class Custodian(TimestampMixin, db.Model):
    """A person accountable for assets. May or may not have a login (user_id)."""

    __tablename__ = "custodians"
    __table_args__ = (db.UniqueConstraint("organisation_id", "staff_id", name="uq_custodian_org_staff"),)

    id = db.Column(db.Integer, primary_key=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey("organisations.id"), nullable=False, index=True)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    full_name = db.Column(db.String(150), nullable=False)
    staff_id = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(40))
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    department = db.relationship("Department")
