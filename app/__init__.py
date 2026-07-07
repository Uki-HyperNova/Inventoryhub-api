from flask import Flask, jsonify

from app.config import Config
from app.extensions import db, jwt, migrate
from app.routes import register_blueprints
from sqlalchemy.exc import OperationalError, ProgrammingError


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from app.models import Product, Sale, SaleItem, User  # noqa: F401

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return db.session.get(User, int(identity))

    register_blueprints(app)

    @app.errorhandler(OperationalError)
    def handle_operational_error(err):
        db.session.rollback()
        orig = getattr(err, "orig", None)
        code = orig.args[0] if orig and orig.args else None
        if code == 1049:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Invalid database name configured.",
                    }
                ),
                500,
            )
        if code in (2003, 2002):
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "MySQL server is not running or not reachable.",
                    }
                ),
                503,
            )
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Database connection failed.",
                }
            ),
            500,
        )

    @app.errorhandler(ProgrammingError)
    def handle_programming_error(err):
        db.session.rollback()
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Invalid database configuration.",
                }
            ),
            500,
        )

    @app.errorhandler(500)
    def handle_internal_error(err):
        return (
            jsonify(
                {
                    "success": False,
                    "message": "An internal server error occurred.",
                }
            ),
            500,
        )

    return app
