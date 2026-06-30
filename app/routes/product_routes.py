from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.controllers import product_contoller as ctrl
from app.middleware import roles_required

product_bp = Blueprint("products", __name__, url_prefix="/api/products")

@product_bp.route("/", methods=["GET"])
# @jwt_required()
def get_all_products():
    return ctrl.get_all_products()

@product_bp.route("/<int:product_id>", methods=["GET"])
# @jwt_required()
def get_product(product_id):
    return ctrl.get_product(product_id)

@product_bp.route("/", methods=["POST"])
# @roles_required("admin")
def create_product():
    return ctrl.create_product()

@product_bp.route("/<int:product_id>", methods=["PUT"])
# @roles_required("admin")
def update_product(product_id):
    return ctrl.update_product(product_id)

@product_bp.route("/<int:product_id>", methods=["DELETE"])
# @roles_required("admin")
def delete_product(product_id):
    return ctrl.delete_product(product_id)