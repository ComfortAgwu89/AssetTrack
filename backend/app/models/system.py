from sqlalchemy import event

from app.extensions import db
from app.models.base import utcnow


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey("organisations.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text)
    link = db.Column(db.String(300))
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)


class AuditLog(db.Model):
    """Append-only. The application refuses UPDATE and DELETE on this table."""

    __tablename__ = "audit_logs"
    __table_args__ = (db.Index("ix_audit_org_created", "organisation_id", "created_at"),)

    id = db.Column(db.Integer, primary_key=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey("organisations.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    action = db.Column(db.String(60), nullable=False)  # e.g. asset.create, auth.login
    entity_type = db.Column(db.String(60))
    entity_id = db.Column(db.Integer)
    summary = db.Column(db.String(300))
    changes = db.Column(db.JSON)  # {"field": {"old": ..., "new": ...}}
    ip_address = db.Column(db.String(64))
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)

    user = db.relationship("User")


@event.listens_for(AuditLog, "before_update")
def _block_audit_update(_mapper, _connection, _target):
    raise PermissionError("Audit log entries cannot be modified.")


@event.listens_for(AuditLog, "before_delete")
def _block_audit_delete(_mapper, _connection, _target):
    raise PermissionError("Audit log entries cannot be deleted.")
