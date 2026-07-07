from datetime import datetime, time

from flask import jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import func

from app.extensions import db
from app.models.product_model import Product
from app.models.sale_model import Sale, SaleItem


def _parse_date_range():
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
def get_dashboard():
    try:
        start_dt, end_dt = _parse_date_range()

        # Aggregate revenue + units sold directly with a database query.
        totals_query = db.session.query(
            func.coalesce(func.sum(Sale.total_amount), 0.0),
            func.coalesce(func.sum(Sale.total_units), 0),
            func.count(Sale.id),
        )
        if start_dt:
            totals_query = totals_query.filter(Sale.created_at >= start_dt)
        if end_dt:
            totals_query = totals_query.filter(Sale.created_at <= end_dt)

        revenue, units_sold, sales_count = totals_query.one()

        low_stock_count = (
            db.session.query(func.count(Product.id))
            .filter(Product.quantity <= Product.low_stock_threshold)
            .scalar()
        )

        total_products = db.session.query(func.count(Product.id)).scalar()

        # Top-selling products (stretch goal chart), grouped/aggregated in SQL.
        top_selling_query = (
            db.session.query(
                SaleItem.product_id,
                SaleItem.product_name,
                func.sum(SaleItem.quantity).label("units_sold"),
                func.sum(SaleItem.subtotal).label("revenue"),
            )
            .join(Sale, Sale.id == SaleItem.sale_id)
        )
        if start_dt:
            top_selling_query = top_selling_query.filter(Sale.created_at >= start_dt)
        if end_dt:
            top_selling_query = top_selling_query.filter(Sale.created_at <= end_dt)

        top_selling = (
            top_selling_query.group_by(SaleItem.product_id, SaleItem.product_name)
            .order_by(func.sum(SaleItem.quantity).desc())
            .limit(5)
            .all()
        )

        low_stock_products = (
            Product.query.filter(Product.quantity <= Product.low_stock_threshold)
            .order_by(Product.quantity.asc())
            .all()
        )

        return jsonify({
            "revenue": float(revenue),
            "units_sold": int(units_sold),
            "sales_count": int(sales_count),
            "total_products": int(total_products),
            "low_stock_count": int(low_stock_count),
            "low_stock_products": [p.to_dict() for p in low_stock_products],
            "top_selling_products": [
                {
                    "product_id": row.product_id,
                    "product_name": row.product_name,
                    "units_sold": int(row.units_sold),
                    "revenue": float(row.revenue),
                }
                for row in top_selling
            ],
        }), 200
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400
    except Exception:
        return jsonify({"error": "An internal server error occurred."}), 500
