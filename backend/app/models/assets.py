from decimal import Decimal

from app.extensions import db
from app.models.base import Money, TimestampMixin, utcnow
from app.services.depreciation import DepreciationParams

ASSET_STATUSES = ("in_use", "in_storage", "under_maintenance", "missing", "disposed")
ASSET_CONDITIONS = ("new", "good", "fair", "poor", "damaged")


class Asset(TimestampMixin, db.Model):
    __tablename__ = "assets"
    __table_args__ = (
        db.UniqueConstraint("organisation_id", "asset_tag", name="uq_asset_org_tag"),
        db.CheckConstraint("acquisition_cost > 0", name="ck_asset_cost_positive"),
        db.CheckConstraint("residual_value >= 0", name="ck_asset_residual_nonneg"),
        db.CheckConstraint("residual_value <= acquisition_cost", name="ck_asset_residual_le_cost"),
        db.CheckConstraint("useful_life_years > 0", name="ck_asset_life_positive"),
        db.CheckConstraint(
            "depreciation_method IN ('straight_line','reducing_balance')", name="ck_asset_method"
        ),
        db.Index("ix_asset_org_status", "organisation_id", "status"),
        db.Index("ix_asset_org_department", "organisation_id", "department_id"),
        db.Index("ix_asset_org_category", "organisation_id", "category_id"),
    )

    id = db.Column(db.Integer, primary_key=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey("organisations.id"), nullable=False)
    asset_tag = db.Column(db.String(40), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("asset_categories.id"), nullable=False)
    description = db.Column(db.Text)
    manufacturer = db.Column(db.String(120))
    model = db.Column(db.String(120))
    serial_number = db.Column(db.String(120))
    supplier = db.Column(db.String(150))

    acquisition_date = db.Column(db.Date, nullable=False)
    acquisition_cost = db.Column(Money, nullable=False)
    residual_value = db.Column(Money, nullable=False, default=0)
    useful_life_years = db.Column(db.Numeric(5, 2), nullable=False)
    depreciation_method = db.Column(db.String(20), nullable=False, default="straight_line")
    depreciation_rate = db.Column(db.Numeric(6, 3))  # percent, reducing balance only
    depreciation_start_date = db.Column(db.Date)

    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"))
    custodian_id = db.Column(db.Integer, db.ForeignKey("custodians.id"))
    condition = db.Column(db.String(20), nullable=False, default="good")
    status = db.Column(db.String(30), nullable=False, default="in_use")
    is_archived = db.Column(db.Boolean, nullable=False, default=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    category = db.relationship("AssetCategory")
    department = db.relationship("Department")
    location = db.relationship("Location")
    custodian = db.relationship("Custodian")

    def depreciation_params(self):
        rate = Decimal(self.depreciation_rate) / 100 if self.depreciation_rate else None
        return DepreciationParams(
            cost=self.acquisition_cost,
            residual=self.residual_value,
            useful_life_years=self.useful_life_years,
            method=self.depreciation_method,
            start_date=self.depreciation_start_date or self.acquisition_date,
            rate=rate,
        )


class AssetAssignment(TimestampMixin, db.Model):
    __tablename__ = "asset_assignments"

    id = db.Column(db.Integer, primary_key=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey("organisations.id"), nullable=False, index=True)
    asset_id = db.Column(db.Integer, db.ForeignKey("assets.id"), nullable=False, index=True)
    custodian_id = db.Column(db.Integer, db.ForeignKey("custodians.id"))
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))
    assigned_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    assigned_on = db.Column(db.Date, nullable=False)
    returned_on = db.Column(db.Date)
    acknowledged_at = db.Column(db.DateTime(timezone=True))
    notes = db.Column(db.Text)


class AssetTransfer(TimestampMixin, db.Model):
    __tablename__ = "asset_transfers"
    __table_args__ = (
        db.CheckConstraint(
            "status IN ('pending','approved','rejected','completed','cancelled')", name="ck_transfer_status"
        ),
        # A transfer can only be completed after someone has reviewed it.
        db.CheckConstraint("status <> 'completed' OR reviewed_by_id IS NOT NULL", name="ck_transfer_needs_approval"),
    )

    id = db.Column(db.Integer, primary_key=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey("organisations.id"), nullable=False, index=True)
    asset_id = db.Column(db.Integer, db.ForeignKey("assets.id"), nullable=False, index=True)
    from_department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))
    to_department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))
    from_location_id = db.Column(db.Integer, db.ForeignKey("locations.id"))
    to_location_id = db.Column(db.Integer, db.ForeignKey("locations.id"))
    from_custodian_id = db.Column(db.Integer, db.ForeignKey("custodians.id"))
    to_custodian_id = db.Column(db.Integer, db.ForeignKey("custodians.id"))
    reason = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    requested_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reviewed_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    reviewed_at = db.Column(db.DateTime(timezone=True))
    review_notes = db.Column(db.Text)
    confirmed_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    confirmed_at = db.Column(db.DateTime(timezone=True))


class DepreciationRecord(db.Model):
    """Immutable posted depreciation snapshot; later edits to the asset never rewrite it."""

    __tablename__ = "depreciation_records"
    __table_args__ = (db.UniqueConstraint("asset_id", "period_end", name="uq_dep_asset_period"),)

    id = db.Column(db.Integer, primary_key=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey("organisations.id"), nullable=False, index=True)
    asset_id = db.Column(db.Integer, db.ForeignKey("assets.id"), nullable=False, index=True)
    period_start = db.Column(db.Date, nullable=False)
    period_end = db.Column(db.Date, nullable=False)
    method = db.Column(db.String(20), nullable=False)
    opening_amount = db.Column(Money, nullable=False)
    expense = db.Column(Money, nullable=False)
    accumulated = db.Column(Money, nullable=False)
    closing_amount = db.Column(Money, nullable=False)
    parameters = db.Column(db.JSON, nullable=False)  # inputs used, for auditability
    posted_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    posted_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)


class MaintenanceRecord(TimestampMixin, db.Model):
    __tablename__ = "maintenance_records"
    __table_args__ = (
        db.CheckConstraint("status IN ('pending','in_progress','completed')", name="ck_maintenance_status"),
    )

    id = db.Column(db.Integer, primary_key=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey("organisations.id"), nullable=False, index=True)
    asset_id = db.Column(db.Integer, db.ForeignKey("assets.id"), nullable=False, index=True)
    issue = db.Column(db.Text, nullable=False)
    reported_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    status = db.Column(db.String(20), nullable=False, default="pending")
    scheduled_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    technician = db.Column(db.String(150))
    work_done = db.Column(db.Text)
    cost = db.Column(Money, nullable=False, default=0)
    condition_after = db.Column(db.String(20))


class VerificationRecord(TimestampMixin, db.Model):
    __tablename__ = "verification_records"

    id = db.Column(db.Integer, primary_key=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey("organisations.id"), nullable=False, index=True)
    asset_id = db.Column(db.Integer, db.ForeignKey("assets.id"), nullable=False, index=True)
    batch_name = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")  # pending|verified|missing|damaged
    found = db.Column(db.Boolean)
    location_confirmed = db.Column(db.Boolean)
    custodian_confirmed = db.Column(db.Boolean)
    condition_found = db.Column(db.String(20))
    verified_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    verified_at = db.Column(db.DateTime(timezone=True))
    notes = db.Column(db.Text)


class DisposalRecord(TimestampMixin, db.Model):
    __tablename__ = "disposal_records"

    id = db.Column(db.Integer, primary_key=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey("organisations.id"), nullable=False, index=True)
    asset_id = db.Column(db.Integer, db.ForeignKey("assets.id"), nullable=False, index=True)
    disposal_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.Text, nullable=False)
    method = db.Column(db.String(40), nullable=False)  # sale | scrap | donation | write_off
    proceeds = db.Column(Money, nullable=False, default=0)
    carrying_amount_at_disposal = db.Column(Money, nullable=False)
    gain_or_loss = db.Column(Money, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    approved_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    approval_reference = db.Column(db.String(120))
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))


class Document(TimestampMixin, db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey("organisations.id"), nullable=False, index=True)
    asset_id = db.Column(db.Integer, db.ForeignKey("assets.id"), index=True)
    kind = db.Column(db.String(20), nullable=False, default="document")  # photo | document
    filename = db.Column(db.String(255), nullable=False)
    content_type = db.Column(db.String(100))
    storage_key = db.Column(db.String(500), nullable=False)
    size_bytes = db.Column(db.Integer)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey("users.id"))
