def register_blueprints(app):
    from app.routes.auth import bp as auth_bp
    from app.routes.dashboard import bp as dashboard_bp
    from app.routes.roles import bp as roles_bp
    from app.routes.health import bp as health_bp

    for blueprint in (health_bp, auth_bp, dashboard_bp, roles_bp):
        app.register_blueprint(blueprint, url_prefix="/api")
