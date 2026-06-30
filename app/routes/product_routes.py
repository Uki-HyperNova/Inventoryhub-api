from flask import Blueprint
from app.controllers import product_contoller as ctrl

auth_bp = Blueprint("product", __name__, url_prefix="/api/product")

@auth_bp.route("/create", methods=["POST"])
def register():
    return ctrl.create_product()

@auth_bp.route("/edit", methods=["UPDATE"])
def login():
    return ctrl.update_product()

@auth_bp.route("/list", methods=["GET"])
def register():
    return ctrl.list_products()

@auth_bp.route("/list/{id}", methods=["GET"])
def register():
    return ctrl.list_product()
