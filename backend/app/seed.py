"""Roles/permissions bootstrap and fictional demo data (a Nigerian university).

Everything here is fictional. Demo accounts share one password taken from the
DEMO_PASSWORD environment variable (falls back to a documented dev value).
"""
import os
from datetime import date

import click

from app.extensions import db
from app.models import (
    Asset, AssetCategory, AuditLog, Custodian, Department, Location, Organisation, Permission, Role, User,
)
from app.services.assets import next_asset_tag
from app.utils.rbac import PERMISSIONS, ROLES

DEMO_ORG_SLUG = "harbourview-university"
DEFAULT_DEMO_PASSWORD = "Demo@12345"

DEMO_USERS = [
    ("super_admin", "Platform Administrator", "superadmin@harbourview.example", None),
    ("org_admin", "Emeka Obi", "admin@harbourview.example", None),
    ("accountant", "Halima Yusuf", "accountant@harbourview.example", None),
    ("asset_manager", "Kemi Balogun", "manager@harbourview.example", None),
    ("department_head", "Prof. Segun Adebayo", "depthead@harbourview.example", "CSC"),
    ("asset_custodian", "Dr. Adaeze Okonkwo", "custodian@harbourview.example", "CSC"),
]

DEPARTMENTS = [
    ("CSC", "Computer Science"), ("ACC", "Accounting"), ("ENG", "Engineering"),
    ("MLS", "Medical Laboratory Science"), ("LIB", "Library Services"), ("EST", "Estate and Works"),
    ("REG", "Registry"), ("PHY", "Physics"),
]

LOCATIONS = {
    "sci": "Science Complex, Room 204", "server": "ICT Centre, Server Room",
    "reg": "Admin Block, Registry Office", "biz": "Business School, Lecture Theatre 1",
    "lib": "Main Library, Ground Floor", "workshop": "Engineering Workshop",
    "garage": "Estate Garage", "mls": "Medical Sciences, Lab 3", "phy": "Physics Laboratory A",
}

# code, name, default life (years), default method
CATEGORIES = [
    ("COMP", "Computer Equipment", 4, "straight_line"), ("FURN", "Office Furniture", 10, "straight_line"),
    ("VEH", "Vehicles", 5, "reducing_balance"), ("LAB", "Laboratory Equipment", 8, "straight_line"),
    ("MACH", "Machinery", 10, "straight_line"), ("BLDG", "Buildings", 40, "straight_line"),
    ("ELEC", "Electrical Equipment", 8, "straight_line"), ("COMM", "Communication Equipment", 5, "straight_line"),
    ("LIBQ", "Library Equipment", 10, "straight_line"),
]

CUSTODIANS = [
    ("Dr. Adaeze Okonkwo", "STF-1001", "CSC"), ("Mr. Tunde Bakare", "STF-1002", "ENG"),
    ("Mrs. Ngozi Eze", "STF-1003", "LIB"), ("Mr. Ibrahim Musa", "STF-1004", "EST"),
    ("Dr. Funmi Adeyemi", "STF-1005", "MLS"), ("Mr. Chidi Nwosu", "STF-1006", "REG"),
]

# name, category, dept, location, custodian idx, cost, residual, life, method, rate %, acquired,
# condition, status, manufacturer, model, supplier
ASSETS = [
    ("Dell Latitude 5440 Laptop", "COMP", "CSC", "sci", 0, 650000, 50000, 4, "straight_line", None, "2023-03-15", "good", "in_use", "Dell", "Latitude 5440", "Techpoint Nigeria Ltd"),
    ("HP LaserJet Pro Printer", "COMP", "REG", "reg", 5, 320000, 20000, 4, "straight_line", None, "2022-06-01", "fair", "in_use", "HP", "LaserJet Pro M404", "Techpoint Nigeria Ltd"),
    ("Computer Laboratory Desktops (20 units)", "COMP", "CSC", "sci", 0, 9800000, 800000, 5, "straight_line", None, "2021-09-10", "good", "in_use", "Lenovo", "ThinkCentre M70", "Zenith Computers"),
    ("Acer Aspire Laptop", "COMP", "ACC", "biz", None, 480000, 40000, 4, "straight_line", None, "2019-02-11", "poor", "in_use", "Acer", "Aspire 5", "Techpoint Nigeria Ltd"),
    ("Dell PowerEdge Server", "COMP", "CSC", "server", 0, 7500000, 500000, 6, "straight_line", None, "2022-01-20", "good", "in_use", "Dell", "PowerEdge R650", "Zenith Computers"),
    ("Lenovo ThinkPad Laptop", "COMP", "ENG", "workshop", 1, 720000, 50000, 4, "straight_line", None, "2025-02-14", "new", "in_use", "Lenovo", "ThinkPad E14", "Zenith Computers"),
    ("Executive Office Desk", "FURN", "REG", "reg", 5, 185000, 15000, 10, "straight_line", None, "2020-05-04", "good", "in_use", "Furnico", "ED-200", "Furnico Nigeria"),
    ("Lecture Theatre Chairs (200 units)", "FURN", "ACC", "biz", None, 6400000, 400000, 10, "straight_line", None, "2018-08-20", "fair", "in_use", "Furnico", "LT-Series", "Furnico Nigeria"),
    ("Library Shelving Units", "LIBQ", "LIB", "lib", 2, 2100000, 100000, 10, "straight_line", None, "2019-11-12", "good", "in_use", "ShelfPro", "SP-900", "Bookwise Supplies"),
    ("Library Barcode Scanners (5 units)", "LIBQ", "LIB", "lib", 2, 380000, 20000, 5, "straight_line", None, "2023-09-09", "good", "in_use", "Zebra", "DS2208", "Bookwise Supplies"),
    ("Toyota Hiace Staff Bus", "VEH", "EST", "garage", 3, 28500000, 3000000, 5, "reducing_balance", 30, "2022-04-18", "good", "in_use", "Toyota", "Hiace 2.7", "CFAO Motors"),
    ("Toyota Hilux Pickup", "VEH", "EST", "garage", 3, 24000000, 2500000, 5, "reducing_balance", None, "2020-10-05", "fair", "under_maintenance", "Toyota", "Hilux 2.8", "CFAO Motors"),
    ("Ford Transit Shuttle", "VEH", "REG", "garage", None, 21000000, 2000000, 5, "reducing_balance", 30, "2019-07-22", "damaged", "in_storage", "Ford", "Transit 350", "Coscharis Motors"),
    ("Digital Oscilloscope", "LAB", "PHY", "phy", None, 1850000, 150000, 8, "straight_line", None, "2021-03-03", "good", "in_use", "Tektronix", "TBS1052B", "LabEquip Africa"),
    ("Laboratory Centrifuge", "LAB", "MLS", "mls", 4, 2750000, 250000, 8, "straight_line", None, "2020-09-14", "good", "in_use", "Eppendorf", "5810R", "LabEquip Africa"),
    ("Biosafety Cabinet Class II", "LAB", "MLS", "mls", 4, 6200000, 500000, 10, "straight_line", None, "2022-02-28", "new", "in_use", "Esco", "Airstream AC2", "LabEquip Africa"),
    ("UV-Vis Spectrophotometer", "LAB", "MLS", "mls", 4, 4300000, 300000, 8, "straight_line", None, "2018-12-01", "fair", "missing", "Shimadzu", "UV-1280", "LabEquip Africa"),
    ("Physics Fume Hood", "LAB", "PHY", "phy", None, 3100000, 200000, 10, "straight_line", None, "2023-12-12", "new", "in_use", "Labconco", "Protector XL", "LabEquip Africa"),
    ("CNC Lathe Machine", "MACH", "ENG", "workshop", 1, 18500000, 1500000, 10, "straight_line", None, "2021-05-17", "good", "in_use", "Haas", "ST-10", "Industrial Tooling Ltd"),
    ("Industrial Welding Machine", "MACH", "ENG", "workshop", 1, 3900000, 300000, 8, "reducing_balance", None, "2019-08-08", "fair", "in_use", "Lincoln Electric", "Power MIG 360", "Industrial Tooling Ltd"),
    ("150kVA Diesel Generator", "ELEC", "EST", "garage", 3, 14500000, 1000000, 10, "straight_line", None, "2020-01-13", "good", "in_use", "Perkins", "150P", "PowerGen Nigeria"),
    ("Split Air Conditioners (10 units)", "ELEC", "ACC", "biz", None, 4200000, 200000, 8, "straight_line", None, "2022-10-10", "good", "in_use", "LG", "Dual Inverter 2HP", "CoolAir Services"),
    ("Solar Inverter System", "ELEC", "ENG", "workshop", 1, 5600000, 400000, 10, "straight_line", None, "2024-03-22", "new", "in_use", "Victron", "Quattro 10kVA", "SunBridge Energy"),
    ("Cisco Network Switch", "COMM", "CSC", "server", 0, 1450000, 100000, 5, "straight_line", None, "2023-07-01", "good", "in_use", "Cisco", "Catalyst 2960-X", "Zenith Computers"),
    ("PABX Telephone System", "COMM", "REG", "reg", 5, 2300000, 200000, 7, "straight_line", None, "2018-04-02", "poor", "in_use", "Panasonic", "KX-NS700", "TeleLink Nigeria"),
    ("Epson Projector", "COMM", "ACC", "biz", None, 520000, 40000, 5, "straight_line", None, "2021-01-25", "fair", "under_maintenance", "Epson", "EB-X49", "Techpoint Nigeria Ltd"),
    ("Administrative Block Building", "BLDG", "REG", "reg", None, 250000000, 25000000, 40, "straight_line", None, "2015-01-05", "good", "in_use", None, None, "Kingsway Construction"),
]


def ensure_roles():
    """Create/refresh permissions and roles from the catalogue in app.utils.rbac (idempotent)."""
    perms = {p.code: p for p in Permission.query.all()}
    for code, desc in PERMISSIONS.items():
        if code not in perms:
            perms[code] = Permission(code=code, description=desc)
            db.session.add(perms[code])
    roles = {r.key: r for r in Role.query.all()}
    for key, spec in ROLES.items():
        role = roles.get(key) or Role(key=key)
        role.name, role.description = spec["name"], spec["description"]
        role.permissions = [perms[c] for c in sorted(spec["permissions"])]
        db.session.add(role)
    db.session.commit()


def seed_demo(password=None):
    """Create the demo organisation. Safe to call once; returns the organisation."""
    ensure_roles()
    existing = Organisation.query.filter_by(slug=DEMO_ORG_SLUG).first()
    if existing:
        return existing
    password = password or os.environ.get("DEMO_PASSWORD") or DEFAULT_DEMO_PASSWORD

    org = Organisation(name="Harbourview University", slug=DEMO_ORG_SLUG, asset_prefix="HVU")
    db.session.add(org)
    db.session.flush()

    depts = {code: Department(organisation_id=org.id, code=code, name=name) for code, name in DEPARTMENTS}
    locs = {k: Location(organisation_id=org.id, name=v) for k, v in LOCATIONS.items()}
    cats = {
        code: AssetCategory(
            organisation_id=org.id, code=code, name=name,
            default_useful_life_years=life, default_depreciation_method=method,
        )
        for code, name, life, method in CATEGORIES
    }
    db.session.add_all([*depts.values(), *locs.values(), *cats.values()])
    db.session.flush()

    roles = {r.key: r for r in Role.query.all()}
    users = {}
    for role_key, full_name, email, dept_code in DEMO_USERS:
        user = User(
            organisation_id=org.id, role_id=roles[role_key].id, full_name=full_name, email=email,
            department_id=depts[dept_code].id if dept_code else None,
        )
        user.set_password(password)
        db.session.add(user)
        users[role_key] = user
    db.session.flush()

    custodians = []
    for name, staff_id, dept_code in CUSTODIANS:
        linked = users["asset_custodian"] if name == users["asset_custodian"].full_name else None
        custodians.append(
            Custodian(
                organisation_id=org.id, department_id=depts[dept_code].id, full_name=name, staff_id=staff_id,
                email=f"{staff_id.lower()}@harbourview.example", user_id=linked.id if linked else None,
            )
        )
    db.session.add_all(custodians)
    db.session.flush()

    manager = users["asset_manager"]
    for (name, cat, dept, loc, cust, cost, residual, life, method, rate, acquired, cond, status,
         maker, model, supplier) in ASSETS:
        acquired_on = date.fromisoformat(acquired)
        asset = Asset(
            organisation_id=org.id, name=name, category_id=cats[cat].id, manufacturer=maker, model=model,
            supplier=supplier, acquisition_date=acquired_on, acquisition_cost=cost, residual_value=residual,
            useful_life_years=life, depreciation_method=method, depreciation_rate=rate,
            depreciation_start_date=acquired_on, department_id=depts[dept].id, location_id=locs[loc].id,
            custodian_id=custodians[cust].id if cust is not None else None,
            condition=cond, status=status, created_by_id=manager.id,
            asset_tag=next_asset_tag(org, cats[cat], acquired_on),
        )
        asset.serial_number = f"SN-{asset.asset_tag}"
        db.session.add(asset)
        db.session.flush()  # keep tag sequence accurate for the next asset
        db.session.add(
            AuditLog(
                organisation_id=org.id, user_id=manager.id, action="asset.create", entity_type="asset",
                entity_id=asset.id, summary=f"Registered {asset.asset_tag} – {asset.name}",
            )
        )
    db.session.commit()
    return org


def register_cli(app):
    @app.cli.command("seed-roles")
    def seed_roles_command():
        """Create or refresh roles and permissions."""
        ensure_roles()
        click.echo("Roles and permissions are up to date.")

    @app.cli.command("seed-demo")
    def seed_demo_command():
        """Load the fictional Harbourview University demo data."""
        seed_demo()
        click.echo("Demo data loaded. See README for demo accounts.")
