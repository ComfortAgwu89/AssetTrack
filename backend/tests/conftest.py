import pytest

DEMO_PASSWORD = "Demo@12345"  # matches app.seed.DEFAULT_DEMO_PASSWORD (tests must not depend on DEMO_PASSWORD env)


@pytest.fixture()
def app(monkeypatch):
    monkeypatch.delenv("DEMO_PASSWORD", raising=False)
    # Imported here so pure-Python tests (e.g. depreciation) run without Flask extensions installed.
    from app import create_app
    from app.extensions import db
    from app.seed import seed_demo

    app = create_app("testing")
    with app.app_context():
        db.create_all()
        seed_demo()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def login(app):
    """Return a test client already signed in as the given demo user."""

    def _login(email):
        c = app.test_client()
        res = c.post("/api/auth/login", json={"email": email, "password": DEMO_PASSWORD})
        assert res.status_code == 200, res.get_json()
        return c

    return _login
