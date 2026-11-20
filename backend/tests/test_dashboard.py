from decimal import Decimal

from app.models import Asset
from app.services.depreciation import compute_position
from datetime import date


def test_dashboard_numbers_come_from_assets(app, login):
    data = login("admin@harbourview.example").get("/api/dashboard").get_json()
    register = Asset.query.filter(Asset.status != "disposed", Asset.is_archived.is_(False)).all()
    k = data["kpis"]
    assert k["total_assets"] == len(register) >= 25
    expected_cost = sum(a.acquisition_cost for a in register)
    assert k["total_acquisition_cost"] == float(expected_cost)
    expected_nbv = sum(compute_position(a.depreciation_params(), date.today()).carrying_amount for a in register)
    assert k["net_book_value"] == float(expected_nbv)
    # reconciliation: cost - accumulated = NBV
    assert round(k["total_acquisition_cost"] - k["accumulated_depreciation"], 2) == k["net_book_value"]


def test_dashboard_breakdowns_reconcile_with_total(login):
    data = login("admin@harbourview.example").get("/api/dashboard").get_json()
    total = data["kpis"]["total_assets"]
    assert sum(r["value"] for r in data["by_department"]) == total
    assert sum(r["value"] for r in data["by_category"]) == total
    assert sum(r["value"] for r in data["by_status"]) == total
    assert round(sum(r["nbv"] for r in data["depreciation_by_category"]), 2) == data["kpis"]["net_book_value"]


def test_dashboard_status_counts(login):
    k = login("admin@harbourview.example").get("/api/dashboard").get_json()["kpis"]
    assert k["missing"] >= 1
    assert k["under_maintenance"] >= 1
    assert k["damaged"] >= 1
    assert k["fully_depreciated"] >= 1


def test_dashboard_filter_by_department(login):
    c = login("admin@harbourview.example")
    full = c.get("/api/dashboard").get_json()
    dept = full["filters"]["departments"][0]
    filtered = c.get(f"/api/dashboard?department_id={dept['id']}").get_json()
    assert filtered["kpis"]["total_assets"] < full["kpis"]["total_assets"]
    assert {r["label"] for r in filtered["by_department"]} <= {dept["name"]}


def test_dashboard_rejects_bad_filter(login):
    c = login("admin@harbourview.example")
    assert c.get("/api/dashboard?department_id=abc").status_code == 400
    assert c.get("/api/dashboard?department_id=99999").status_code == 404


def test_department_head_only_sees_own_department(login):
    full = login("admin@harbourview.example").get("/api/dashboard").get_json()["kpis"]["total_assets"]
    data = login("depthead@harbourview.example").get("/api/dashboard").get_json()
    assert 0 < data["kpis"]["total_assets"] < full
    assert [r["label"] for r in data["by_department"]] == ["Computer Science"]
    assert data["recent_activity"] == []  # no org-wide activity for this role


def test_custodian_only_sees_assigned_assets(login):
    full = login("admin@harbourview.example").get("/api/dashboard").get_json()["kpis"]["total_assets"]
    data = login("custodian@harbourview.example").get("/api/dashboard").get_json()
    assert 0 < data["kpis"]["total_assets"] < full


def test_new_organisation_cannot_see_other_organisation_data(client):
    client.post(
        "/api/auth/register",
        json={
            "organisation_name": "Isolated Org", "full_name": "Iso Lated",
            "email": "iso@isolated.example", "password": "Strong123pass",
        },
    )
    data = client.get("/api/dashboard").get_json()
    assert data["kpis"]["total_assets"] == 0
    assert data["kpis"]["total_acquisition_cost"] == 0
    assert data["filters"]["departments"] == []


def test_cannot_filter_by_another_organisations_department(app, login, client):
    demo_dept = login("admin@harbourview.example").get("/api/dashboard").get_json()["filters"]["departments"][0]["id"]
    client.post(
        "/api/auth/register",
        json={
            "organisation_name": "Other Org", "full_name": "Oth Er",
            "email": "other@other.example", "password": "Strong123pass",
        },
    )
    assert client.get(f"/api/dashboard?department_id={demo_dept}").status_code == 404


def test_database_enforces_accounting_constraints(app):
    from sqlalchemy.exc import IntegrityError
    from app.extensions import db

    base = Asset.query.first()
    for bad in ({"acquisition_cost": Decimal("0")}, {"residual_value": base.acquisition_cost + 1}, {"useful_life_years": 0}):
        values = dict(
            organisation_id=base.organisation_id, name="Bad", category_id=base.category_id,
            acquisition_date=date(2024, 1, 1), acquisition_cost=Decimal("1000"), residual_value=Decimal("100"),
            useful_life_years=5, asset_tag=f"BAD-{len(bad)}-{list(bad)[0]}",
        )
        values.update(bad)
        db.session.add(Asset(**values))
        try:
            db.session.commit()
            raised = False
        except IntegrityError:
            raised = True
            db.session.rollback()
        assert raised, bad
