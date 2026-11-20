"""AssetTrack Flask application factory.

Imports are kept inside create_app so pure-Python modules (for example
app.services.depreciation) can be imported and tested without Flask extensions.
"""


def create_app(config_name=None):
    from flask import Flask, jsonify
    from werkzeug.exceptions import HTTPException

    from app.extensions import db, jwt, migrate
    from config import get_config

    app = Flask(__name__)
    app.config.from_object(get_config(config_name))

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    from app import models  # noqa: F401  (register models for migrations)
    from app.routes import register_blueprints

    register_blueprints(app)

    @jwt.unauthorized_loader
    @jwt.invalid_token_loader
    def _unauthorised(reason):
        return jsonify(error={"message": "Authentication required.", "details": reason}), 401

    @jwt.expired_token_loader
    def _expired(_header, _payload):
        return jsonify(error={"message": "Session expired. Please sign in again."}), 401

    @app.errorhandler(HTTPException)
    def _http_error(err):
        return jsonify(error={"message": err.description}), err.code

    @app.errorhandler(Exception)
    def _unhandled(err):
        app.logger.exception("Unhandled error")
        return jsonify(error={"message": "Internal server error."}), 500

    from app.seed import register_cli

    register_cli(app)
    return app
