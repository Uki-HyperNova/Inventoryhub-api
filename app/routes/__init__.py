from app.routes.auth_routes import auth_bp
from app.routes.product_routes import product_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)