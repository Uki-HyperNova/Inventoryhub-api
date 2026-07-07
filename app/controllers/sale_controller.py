from datetime import datetime, timezone

from flask import request
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from app.extensions import db
from app.models.product_model import Product
from app.models.sale_model import Sale, SaleItem
from app.utils.responses import error_response, success_response


def _validate_sale_payload(data: dict | None) -> dict[str, list[str]]:
    errors: dict[str, list[str]] = {}

    if not data:
        return {"_schema": ["Request body is required."]}

    items = data.get("items")
    if items is None:
        errors.setdefault("items", []).append("Items are required.")
    elif not isinstance(items, list) or len(items) == 0:
        errors.setdefault("items", []).append("At least one item is required.")

    return errors


def _generate_invoice_number() -> str:
    return f"INV-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"


@jwt_required()
def record_sale():
    data = request.get_json(silent=True)
    errors = _validate_sale_payload(data)
    if errors:
        return error_response("Validation failed.", errors, 400)

    items_data = data["items"]

    try:
        validated_items: list[tuple[Product, int]] = []

        for index, item in enumerate(items_data):
            product_id = item.get("product_id")
            quantity = item.get("quantity")

            if product_id is None or quantity is None:
                return error_response(
                    "Validation failed.",
                    {
                        "items": [
                            f"Item at index {index} must include product_id and quantity."
                        ]
                    },
                    400,
                )

            try:
                quantity_int = int(quantity)
            except (TypeError, ValueError):
                return error_response(
                    "Validation failed.",
                    {"items": ["Quantity must be a whole number."]},
                    400,
                )

            if quantity_int <= 0:
                return error_response(
                    "Validation failed.",
                    {"items": ["Quantity must be greater than 0."]},
                    400,
                )

            product = db.session.get(Product, int(product_id))
            if not product:
                return error_response(f"Product {product_id} not found.", status=404)

            if product.quantity < quantity_int:
                return error_response(
                    f"Insufficient stock for {product.name}. "
                    f"Available: {product.quantity}, requested: {quantity_int}.",
                    status=400,
                )

            validated_items.append((product, quantity_int))

        total_amount = 0.0
        sale = Sale(
            invoice_number=_generate_invoice_number(),
            total_amount=0,
        )
        db.session.add(sale)
        db.session.flush()

        for product, quantity_int in validated_items:
            subtotal = round(product.price * quantity_int, 2)
            total_amount += subtotal
            product.quantity -= quantity_int

            db.session.add(
                SaleItem(
                    sale_id=sale.id,
                    product_id=product.id,
                    quantity=quantity_int,
                    unit_price=product.price,
                    subtotal=subtotal,
                )
            )

        sale.total_amount = round(total_amount, 2)
        db.session.commit()

        return success_response(
            "Sale recorded successfully.",
            {"sale": sale.to_dict()},
            201,
        )
    except Exception:
        db.session.rollback()
        return error_response("An internal server error occurred.", status=500)


@jwt_required()
def list_sales():
    try:
        search = request.args.get("search", "").strip().lower()
        page = max(int(request.args.get("page", 1)), 1)
        per_page = min(max(int(request.args.get("per_page", 10)), 1), 100)

        query = Sale.query.order_by(Sale.created_at.desc(), Sale.id.desc())

        if search:
            query = query.filter(
                func.lower(Sale.invoice_number).like(f"%{search.lower()}%")
            )

        total = query.count()
        sales = query.offset((page - 1) * per_page).limit(per_page).all()

        return success_response(
            "Sales fetched successfully.",
            {
                "sales": [sale.to_dict() for sale in sales],
                "total": total,
                "page": page,
                "per_page": per_page,
            },
        )
    except Exception:
        return error_response("An internal server error occurred.", status=500)
