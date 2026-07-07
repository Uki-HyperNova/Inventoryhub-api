from flask import request
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.product_model import Product
from app.utils.responses import error_response, success_response


def _validate_product_payload(data, partial=False):
    errors: dict[str, list[str]] = {}

    if not data:
        return {"_schema": ["Request body is required."]}

    if "name" in data or not partial:
        name = data.get("name")
        if name is None or str(name).strip() == "":
            errors.setdefault("name", []).append("Name is required.")

    if "sku" in data or not partial:
        sku = data.get("sku")
        if sku is None or str(sku).strip() == "":
            errors.setdefault("sku", []).append("SKU is required.")

    if "category" in data or not partial:
        category = data.get("category")
        if category is None or str(category).strip() == "":
            errors.setdefault("category", []).append("Category is required.")

    if "price" in data or not partial:
        price = data.get("price")
        if price is None:
            errors.setdefault("price", []).append("Price is required.")
        else:
            try:
                price_val = float(price)
                if price_val < 0:
                    errors.setdefault("price", []).append("Price cannot be negative.")
            except (TypeError, ValueError):
                errors.setdefault("price", []).append("Price must be a number.")

    if "quantity" in data or not partial:
        quantity = data.get("quantity")
        if quantity is None:
            errors.setdefault("quantity", []).append("Quantity is required.")
        else:
            try:
                qty_val = int(quantity)
                if qty_val < 0:
                    errors.setdefault("quantity", []).append("Quantity cannot be negative.")
            except (TypeError, ValueError):
                errors.setdefault("quantity", []).append("Quantity must be a whole number.")

    if "low_stock_threshold" in data or not partial:
        threshold = data.get("low_stock_threshold")
        if threshold is None and not partial:
            pass
        elif threshold is not None:
            try:
                threshold_val = int(threshold)
                if threshold_val < 0:
                    errors.setdefault("low_stock_threshold", []).append(
                        "Low stock threshold cannot be negative."
                    )
            except (TypeError, ValueError):
                errors.setdefault("low_stock_threshold", []).append(
                    "Low stock threshold must be a whole number."
                )

    return errors


@jwt_required()
def create_product():
    data = request.get_json(silent=True)
    errors = _validate_product_payload(data)
    if errors:
        return error_response("Validation failed.", errors, 400)

    try:
        product = Product(
            name=str(data.get("name")).strip(),
            sku=str(data.get("sku")).strip(),
            category=str(data.get("category")).strip(),
            price=float(data.get("price")),
            quantity=int(data.get("quantity")),
            low_stock_threshold=int(data.get("low_stock_threshold", 10)),
        )
        db.session.add(product)
        db.session.commit()
        return success_response(
            "Product created successfully.",
            {"product": product.to_dict()},
            201,
        )
    except IntegrityError:
        db.session.rollback()
        return error_response(
            "SKU must be unique.",
            {"sku": ["This SKU is already in use."]},
            409,
        )
    except Exception:
        db.session.rollback()
        return error_response("An internal server error occurred.", status=500)


@jwt_required()
def update_product(id):
    product = db.session.get(Product, id)
    if not product:
        return error_response("Product not found.", status=404)

    data = request.get_json(silent=True)
    errors = _validate_product_payload(data, partial=True)
    if errors:
        return error_response("Validation failed.", errors, 400)

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
        if "low_stock_threshold" in data:
            product.low_stock_threshold = int(data.get("low_stock_threshold"))

        db.session.commit()
        return success_response(
            "Product updated successfully.",
            {"product": product.to_dict()},
        )
    except IntegrityError:
        db.session.rollback()
        return error_response(
            "SKU must be unique.",
            {"sku": ["This SKU is already in use."]},
            409,
        )
    except Exception:
        db.session.rollback()
        return error_response("An internal server error occurred.", status=500)


@jwt_required()
def delete_product(id):
    product = db.session.get(Product, id)
    if not product:
        return error_response("Product not found.", status=404)

    try:
        db.session.delete(product)
        db.session.commit()
        return success_response("Product deleted successfully.")
    except Exception:
        db.session.rollback()
        return error_response("An internal server error occurred.", status=500)


@jwt_required()
def list_products():
    try:
        products = Product.query.order_by(Product.id.desc()).all()
        return success_response(
            "Products fetched successfully.",
            {"products": [p.to_dict() for p in products]},
        )
    except Exception:
        return error_response("An internal server error occurred.", status=500)


@jwt_required()
def get_product(id):
    product = db.session.get(Product, id)
    if not product:
        return error_response("Product not found.", status=404)
    return success_response(
        "Product fetched successfully.",
        {"product": product.to_dict()},
    )
