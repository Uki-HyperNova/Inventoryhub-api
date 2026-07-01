from flask import Blueprint
from app.controllers import product_contoller as ctrl

product_bp = Blueprint("product", __name__, url_prefix="/api/products")

@product_bp.route("", methods=["POST"])
def create_product():
    return ctrl.create_product()

@product_bp.route("", methods=["GET"])
def list_products():
    return ctrl.list_products()

@product_bp.route("/<int:id>", methods=["GET"])
def get_product(id):
    return ctrl.get_product(id)

@product_bp.route("/<int:id>", methods=["PUT"])
def update_product(id):
    return ctrl.update_product(id)

@product_bp.route("/<int:id>", methods=["DELETE"])
def delete_product(id):
    return ctrl.delete_product(id)
