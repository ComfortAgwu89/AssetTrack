"""Application configuration. All secrets come from environment variables."""
import os
from datetime import timedelta


def _database_url():
    url = os.environ.get("DATABASE_URL", "postgresql+psycopg2://localhost/assettrack")
    # Render and some hosts supply the legacy "postgres://" scheme.
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    return url


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-insecure-key")
    SQLALCHEMY_DATABASE_URI = _database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT stored in an httpOnly cookie, protected by double-submit CSRF token.
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-only-insecure-jwt-key")
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = os.environ.get("JWT_COOKIE_SECURE", "false").lower() == "true"
    JWT_COOKIE_SAMESITE = "Lax"
    JWT_COOKIE_CSRF_PROTECT = True
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    JWT_COOKIE_CSRF_PROTECT = False
    SECRET_KEY = "test-secret"
    JWT_SECRET_KEY = "test-jwt-secret-that-is-long-enough-for-hs256"


class ProductionConfig(Config):
    DEBUG = False
    JWT_COOKIE_SECURE = True

    @classmethod
    def validate(cls):
        if cls.SECRET_KEY.startswith("dev-only") or cls.JWT_SECRET_KEY.startswith("dev-only"):
            raise RuntimeError("SECRET_KEY and JWT_SECRET_KEY must be set in production.")


CONFIGS = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(name=None):
    name = name or os.environ.get("FLASK_ENV", "development")
    cfg = CONFIGS.get(name, DevelopmentConfig)
    if hasattr(cfg, "validate"):
        cfg.validate()
    return cfg
