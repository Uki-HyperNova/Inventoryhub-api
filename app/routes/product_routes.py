from flask import Blueprint
from app.controllers import product_contoller as ctrl
from flask_jwt_extended import jwt_required


product_bp = Blueprint("product", __name__, url_prefix="/api/products")

@product_bp.route("", methods=["POST"])
@jwt_required()

def create_product():
    return ctrl.create_product()

@product_bp.route("", methods=["GET"])
@jwt_required()

def list_products():
    return ctrl.list_products()

@product_bp.route("/<int:id>", methods=["GET"])
@jwt_required()

def get_product(id):
    return ctrl.get_product(id)

@product_bp.route("/<int:id>", methods=["PUT"])
@jwt_required()

def update_product(id):
    return ctrl.update_product(id)

@product_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()

def delete_product(id):
    return ctrl.delete_product(id)

@product_bp.route("/<int:id>/restock", methods=["PUT"])
@jwt_required()

def restock_product(id):
    return ctrl.restock_product(id)
