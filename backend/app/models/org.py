from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from app.models.base import TimestampMixin

role_permissions = db.Table(
    "role_permissions",
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    db.Column("permission_id", db.Integer, db.ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True),
)


class Organisation(TimestampMixin, db.Model):
    __tablename__ = "organisations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    asset_prefix = db.Column(db.String(8), nullable=False, default="AST")
    currency_code = db.Column(db.String(3), nullable=False, default="NGN")
    currency_symbol = db.Column(db.String(4), nullable=False, default="₦")
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class Permission(db.Model):
    __tablename__ = "permissions"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(60), unique=True, nullable=False)
    description = db.Column(db.String(200))


class Role(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(40), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(300))
    permissions = db.relationship("Permission", secondary=role_permissions, lazy="selectin")

    @property
    def permission_codes(self):
        return {p.code for p in self.permissions}


class User(TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    organisation_id = db.Column(db.Integer, db.ForeignKey("organisations.id"), nullable=False, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"))
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(40))
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    last_login_at = db.Column(db.DateTime(timezone=True))

    organisation = db.relationship("Organisation")
    role = db.relationship("Role", lazy="joined")
    department = db.relationship("Department", foreign_keys=[department_id])

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def has_permission(self, code):
        return code in self.role.permission_codes

    def to_dict(self):
        org = self.organisation
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "role": {"key": self.role.key, "name": self.role.name},
            "permissions": sorted(self.role.permission_codes),
            "department_id": self.department_id,
            "organisation": {
                "id": org.id,
                "name": org.name,
                "currency_code": org.currency_code,
                "currency_symbol": org.currency_symbol,
            },
        }
