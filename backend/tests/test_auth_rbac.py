from app.extensions import db
from app.models import AuditLog


def test_login_success_returns_user_and_permissions(client):
    res = client.post("/api/auth/login", json={"email": "admin@harbourview.example", "password": "Demo@12345"})
    assert res.status_code == 200
    user = res.get_json()["user"]
    assert user["role"]["key"] == "org_admin"
    assert "user.manage" in user["permissions"]


def test_login_wrong_password_is_rejected(client):
    res = client.post("/api/auth/login", json={"email": "admin@harbourview.example", "password": "nope"})
    assert res.status_code == 401


def test_protected_endpoint_requires_login(client):
    assert client.get("/api/dashboard").status_code == 401
    assert client.get("/api/auth/me").status_code == 401


def test_logout_clears_session(login):
    c = login("admin@harbourview.example")
    assert c.get("/api/auth/me").status_code == 200
    c.post("/api/auth/logout")
    assert c.get("/api/auth/me").status_code == 401


def test_roles_endpoint_limited_to_user_managers(login):
    assert login("admin@harbourview.example").get("/api/roles").status_code == 200
    assert login("custodian@harbourview.example").get("/api/roles").status_code == 403
    assert login("accountant@harbourview.example").get("/api/roles").status_code == 403


def test_org_admin_cannot_see_super_admin_role(login):
    keys = [r["key"] for r in login("admin@harbourview.example").get("/api/roles").get_json()["roles"]]
    assert "super_admin" not in keys
    keys = [r["key"] for r in login("superadmin@harbourview.example").get("/api/roles").get_json()["roles"]]
    assert "super_admin" in keys


def test_register_creates_org_and_admin(client):
    res = client.post(
        "/api/auth/register",
        json={
            "organisation_name": "Green Valley Hospital",
            "full_name": "Ada Obi",
            "email": "ada@greenvalley.example",
            "password": "Strong123pass",
        },
    )
    assert res.status_code == 201
    assert res.get_json()["user"]["role"]["key"] == "org_admin"


def test_register_validates_input(client):
    res = client.post("/api/auth/register", json={"email": "bad", "password": "short"})
    assert res.status_code == 422
    assert {"organisation_name", "full_name", "email", "password"} <= set(res.get_json()["error"]["details"])


def test_register_rejects_duplicate_email(client):
    res = client.post(
        "/api/auth/register",
        json={
            "organisation_name": "Copycat", "full_name": "Copy Cat",
            "email": "admin@harbourview.example", "password": "Strong123pass",
        },
    )
    assert res.status_code == 422


def test_audit_log_cannot_be_modified_or_deleted(app):
    entry = AuditLog.query.first()
    entry.summary = "tampered"
    try:
        db.session.commit()
        raised = False
    except PermissionError:
        raised = True
        db.session.rollback()
    assert raised

    db.session.delete(AuditLog.query.first())
    try:
        db.session.commit()
        raised = False
    except PermissionError:
        raised = True
        db.session.rollback()
    assert raised
