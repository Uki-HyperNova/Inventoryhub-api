from flask import Blueprint
from app.controllers import dashboard_controller as ctrl
from flask_jwt_extended import jwt_required


dashboard_bp = Blueprint("dashboard", __name__, url_prefix="/api/dashboard")

@dashboard_bp.route("", methods=["GET"])
@jwt_required()

def get_dashboard():
    return ctrl.get_dashboard()
