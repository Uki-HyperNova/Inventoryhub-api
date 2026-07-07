from flask import Blueprint
from app.controllers import sale_controller as ctrl
from flask_jwt_extended import jwt_required


sale_bp = Blueprint("sale", __name__, url_prefix="/api/sales")

@sale_bp.route("", methods=["POST"])
@jwt_required()

def create_sale():
    return ctrl.create_sale()

@sale_bp.route("", methods=["GET"])
@jwt_required()

def list_sales():
    return ctrl.list_sales()

@sale_bp.route("/<int:id>", methods=["GET"])
@jwt_required()

def get_sale(id):
    return ctrl.get_sale(id)
