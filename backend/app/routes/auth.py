import re
from datetime import datetime, timezone

from flask import Blueprint, g, jsonify, request
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies

from app.extensions import db
from app.models import Organisation, Role, User
from app.seed import ensure_roles
from app.utils.audit import log_action
from app.utils.rbac import error_response, require_permission

bp = Blueprint("auth", __name__, url_prefix="/auth")

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "org"


def _prefix(name):
    letters = "".join(w[0] for w in re.findall(r"[A-Za-z]+", name))[:4].upper()
    return letters or "ORG"


def _password_errors(password):
    problems = []
    if len(password) < 8:
        problems.append("at least 8 characters")
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        problems.append("a mix of letters and numbers")
    return problems


@bp.post("/register")
def register():
    """Create a new organisation together with its first Organisation Administrator."""
    data = request.get_json(silent=True) or {}
    org_name = (data.get("organisation_name") or "").strip()
    full_name = (data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    errors = {}
    if len(org_name) < 2:
        errors["organisation_name"] = "Enter your organisation's name."
    if len(full_name) < 2:
        errors["full_name"] = "Enter your full name."
    if not EMAIL_RE.match(email):
        errors["email"] = "Enter a valid email address."
    elif User.query.filter_by(email=email).first():
        errors["email"] = "An account with this email already exists."
    problems = _password_errors(password)
    if problems:
        errors["password"] = "Password needs " + " and ".join(problems) + "."
    if errors:
        return error_response("Please correct the highlighted fields.", 422, errors)

    ensure_roles()
    role = Role.query.filter_by(key="org_admin").one()

    base_slug, slug, n = _slugify(org_name), None, 1
    slug = base_slug
    while Organisation.query.filter_by(slug=slug).first():
        n += 1
        slug = f"{base_slug}-{n}"

    org = Organisation(name=org_name, slug=slug, asset_prefix=_prefix(org_name))
    db.session.add(org)
    db.session.flush()
    user = User(organisation_id=org.id, role_id=role.id, full_name=full_name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()
    log_action("organisation.create", org.id, user, "organisation", org.id, f"Organisation '{org.name}' registered")
    db.session.commit()

    return _session_response(user, 201)


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return error_response("Enter your email and password.", 422)

    user = User.query.filter_by(email=email).first()
    if user is None or not user.check_password(password):
        return error_response("Incorrect email or password.", 401)
    if not user.is_active or not user.organisation.is_active:
        return error_response("This account has been deactivated.", 403)

    user.last_login_at = datetime.now(timezone.utc)
    log_action("auth.login", user.organisation_id, user, "user", user.id, f"{user.full_name} signed in")
    db.session.commit()
    return _session_response(user, 200)


@bp.post("/logout")
def logout():
    response = jsonify(message="Signed out.")
    unset_jwt_cookies(response)
    return response


@bp.get("/me")
@require_permission()
def me():
    return jsonify(user=g.current_user.to_dict())


def _session_response(user, status):
    response = jsonify(user=user.to_dict())
    set_access_cookies(response, create_access_token(identity=str(user.id)))
    response.status_code = status
    return response
