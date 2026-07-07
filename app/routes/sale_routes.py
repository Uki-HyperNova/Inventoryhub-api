from flask import Blueprint

from app.controllers import sale_controller as ctrl

sale_bp = Blueprint("sales", __name__, url_prefix="/api/sales")


@sale_bp.route("", methods=["GET"])
def list_sales():
    return ctrl.list_sales()


@sale_bp.route("", methods=["POST"])
def record_sale():
    return ctrl.record_sale()
