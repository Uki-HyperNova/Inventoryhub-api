from flask import jsonify, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.product_model import Product
from app.utils import get_json_body


def _validate_product_payload(data, partial=False):
    errors =[]

    if not data:
        return ["Request body is required."]

    if "name" in data or not partial:
        name = data.get("name")
        if name is None or str(name).strip() == "":
            errors.append("name is required.")

    if "sku" in data or not partial:
        sku = data.get("sku")
        if sku is None or str(sku).strip() == "":
            errors.append("sku is required.")

    if "category" in data or not partial:
        category = data.get("category")
        if category is None or str(category).strip() == "":
            errors.append("category is required.")

    if "price" in data or not partial:
        price = data.get("price")
        if price is None:
            errors.append("price is required.")
        else:
            try:
                float(price)
            except (TypeError, ValueError):
                errors.append("price must be a number.")

    if "quantity" in data or not partial:
        quantity = data.get("quantity")
        if quantity is None:
            errors.append("quantity is required.")
        else:
            try:
                int(quantity)
            except (TypeError, ValueError):
                errors.append("quantity must be a whole number.")

    if "low_stock_threshold" in data and data.get("low_stock_threshold") is not None:
        try:
            int(data.get("low_stock_threshold"))
        except (TypeError, ValueError):
            errors.append("low_stock_threshold must be a whole number.")

    return errors


def create_product():
    data = get_json_body()
    errors = _validate_product_payload(data)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        product = Product(
            name=str(data.get("name")).strip(),
            sku=str(data.get("sku")).strip(),
            category=str(data.get("category")).strip(),
            price=float(data.get("price")),
            quantity=int(data.get("quantity")),
            low_stock_threshold=int(data.get("low_stock_threshold")) if data.get("low_stock_threshold") is not None else 5,
        )
        db.session.add(product)
        db.session.commit()
        return jsonify({"message": "Product created successfully.", "product": product.to_dict()}), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred."}), 500


@jwt_required()
def update_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({"error": "Product not found."}), 404

    data = get_json_body()
    errors = _validate_product_payload(data, partial=True)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        if "name" in data:
            product.name = str(data.get("name")).strip()
        if "sku" in data:
            product.sku = str(data.get("sku")).strip()
        if "category" in data:
            product.category = str(data.get("category")).strip()
        if "price" in data:
            product.price = float(data.get("price"))
        if "quantity" in data:
            product.quantity = int(data.get("quantity"))
        if "low_stock_threshold" in data and data.get("low_stock_threshold") is not None:
            product.low_stock_threshold = int(data.get("low_stock_threshold"))

        db.session.commit()
        return jsonify({"message": "Product updated successfully.", "product": product.to_dict()}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred."}), 500


@jwt_required()
def delete_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({"error": "Product not found."}), 404

    try:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully."}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred."}), 500


@jwt_required()
def restock_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({"error": "Product not found."}), 404

    data = get_json_body()
    if not data:
        return jsonify({"error": "Request body is required."}), 400

    quantity = data.get("quantity")
    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        return jsonify({"errors": ["quantity must be a whole number."]}), 400

    if quantity <= 0:
        return jsonify({"errors": ["quantity must be greater than zero."]}), 400

    try:
        product.quantity += quantity
        db.session.commit()
        return jsonify({"message": "Product restocked successfully.", "product": product.to_dict()}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred."}), 500


@jwt_required()
def list_products():
    try:
        products = Product.query.order_by(Product.id.desc()).all()
        return jsonify({"products": [p.to_dict() for p in products]}), 200
    except Exception:
        return jsonify({"error": "An internal server error occurred."}), 500


@jwt_required()
def get_product(id):
    product = db.session.get(Product, id)
    if not product:
        return jsonify({"error": "Product not found."}), 404
    return jsonify({"product": product.to_dict()}), 200
