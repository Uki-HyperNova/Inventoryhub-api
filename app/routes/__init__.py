from app.routes.auth_routes import auth_bp
from app.routes.product_routes import product_bp
from app.routes.sale_routes import sale_bp
from app.routes.dashboard_routes import dashboard_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(sale_bp)
    app.register_blueprint(dashboard_bp)