from datetime import datetime, time

from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.product_model import Product
from app.models.sale_model import Sale, SaleItem
from app.utils import get_json_body


def _validate_sale_payload(data):
    errors = []

    if not data:
        return ["Request body is required."]

    items = data.get("items")
    if not items or not isinstance(items, list):
        errors.append("items is required and must be a non-empty list.")
        return errors

    for idx, item in enumerate(items):
        product_id = item.get("product_id")
        quantity = item.get("quantity")

        if product_id is None:
            errors.append(f"items[{idx}].product_id is required.")
        if quantity is None:
            errors.append(f"items[{idx}].quantity is required.")
        else:
            try:
                if int(quantity) <= 0:
                    errors.append(f"items[{idx}].quantity must be greater than zero.")
            except (TypeError, ValueError):
                errors.append(f"items[{idx}].quantity must be a whole number.")

    return errors


@jwt_required()
def create_sale():
    data = get_json_body()
    errors = _validate_sale_payload(data)
    if errors:
        return jsonify({"errors": errors}), 400

    items_payload = data.get("items")

    try:
        # Lock in the products first and validate stock availability across
        # every line item before mutating anything.
        resolved_items = []
        for item in items_payload:
            product = db.session.get(Product, int(item.get("product_id")))
            quantity = int(item.get("quantity"))

            if not product:
                return jsonify({"error": f"Product {item.get('product_id')} not found."}), 404

            if product.quantity < quantity:
                return jsonify({
                    "error": f"Insufficient stock for '{product.name}'. Available: {product.quantity}, requested: {quantity}."
                }), 400

            resolved_items.append((product, quantity))

        staff_id = get_jwt_identity()
        sale = Sale(staff_id=int(staff_id) if staff_id else None, total_amount=0, total_units=0)
        db.session.add(sale)
        db.session.flush()  # get sale.id before committing

        total_amount = 0.0
        total_units = 0

        for product, quantity in resolved_items:
            # This is the signature logic: reduce stock, and the low-stock
            # flag is automatically derived from quantity vs threshold.
            product.quantity -= quantity

            subtotal = round(product.price * quantity, 2)
            total_amount += subtotal
            total_units += quantity

            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=product.id,
                product_name=product.name,
                quantity=quantity,
                unit_price=product.price,
                subtotal=subtotal,
            )
            db.session.add(sale_item)

        sale.total_amount = round(total_amount, 2)
        sale.total_units = total_units

        db.session.commit()
        return jsonify({"message": "Sale recorded successfully.", "sale": sale.to_dict()}), 201
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred."}), 500


def _parse_date_range():
    """Parses optional ?from=YYYY-MM-DD&to=YYYY-MM-DD query params."""
    date_from = request.args.get("from")
    date_to = request.args.get("to")

    start_dt = None
    end_dt = None

    if date_from:
        start_dt = datetime.combine(datetime.strptime(date_from, "%Y-%m-%d").date(), time.min)
    if date_to:
        end_dt = datetime.combine(datetime.strptime(date_to, "%Y-%m-%d").date(), time.max)

    return start_dt, end_dt


@jwt_required()
def list_sales():
    try:
        query = Sale.query
        start_dt, end_dt = _parse_date_range()

        if start_dt:
            query = query.filter(Sale.created_at >= start_dt)
        if end_dt:
            query = query.filter(Sale.created_at <= end_dt)

        sales = query.order_by(Sale.created_at.desc()).all()
        return jsonify({"sales": [s.to_dict() for s in sales]}), 200
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    except Exception:
        return jsonify({"error": "An internal server error occurred."}), 500


@jwt_required()
def get_sale(id):
    sale = db.session.get(Sale, id)
    if not sale:
        return jsonify({"error": "Sale not found."}), 404
    return jsonify({"sale": sale.to_dict()}), 200
