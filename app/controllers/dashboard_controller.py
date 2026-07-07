from collections import defaultdict
from datetime import timedelta

from flask_jwt_extended import jwt_required
from sqlalchemy import func

from app.extensions import db
from app.models.product_model import Product
from app.models.sale_model import Sale, SaleItem
from app.utils import utc_now
from app.utils.responses import error_response, success_response


@jwt_required()
def get_dashboard():
    try:
        products = Product.query.all()
        total_products = len(products)

        low_stock_items = [p.to_dict() for p in products if p.is_low_stock()]
        low_stock_products = len(low_stock_items)

        total_revenue = (
            db.session.query(func.coalesce(func.sum(Sale.total_amount), 0.0)).scalar()
            or 0.0
        )

        units_sold = (
            db.session.query(func.coalesce(func.sum(SaleItem.quantity), 0)).scalar() or 0
        )

        now = utc_now()
        chart_start = now - timedelta(days=6)
        recent_sales_rows = (
            Sale.query.filter(Sale.created_at >= chart_start)
            .order_by(Sale.created_at.asc())
            .all()
        )

        revenue_by_date: dict[str, float] = defaultdict(float)
        for sale in recent_sales_rows:
            date_key = sale.created_at.date().isoformat()
            revenue_by_date[date_key] += sale.total_amount

        revenue_chart = []
        for offset in range(7):
            day = (chart_start + timedelta(days=offset)).date()
            date_key = day.isoformat()
            revenue_chart.append(
                {
                    "date": date_key,
                    "revenue": round(revenue_by_date.get(date_key, 0.0), 2),
                }
            )

        top_rows = (
            db.session.query(
                Product.name.label("name"),
                func.sum(SaleItem.quantity).label("quantity"),
                func.sum(SaleItem.subtotal).label("revenue"),
            )
            .join(Product, Product.id == SaleItem.product_id)
            .group_by(Product.name)
            .order_by(func.sum(SaleItem.quantity).desc())
            .limit(5)
            .all()
        )

        top_selling_products = [
            {
                "name": row.name,
                "quantity": int(row.quantity or 0),
                "revenue": round(float(row.revenue or 0.0), 2),
            }
            for row in top_rows
        ]

        recent_sales = (
            Sale.query.order_by(Sale.created_at.desc(), Sale.id.desc()).limit(5).all()
        )

        dashboard = {
            "total_revenue": round(float(total_revenue), 2),
            "total_products": total_products,
            "units_sold": int(units_sold),
            "low_stock_products": low_stock_products,
            "revenue_chart": revenue_chart,
            "top_selling_products": top_selling_products,
            "recent_sales": [sale.to_dict() for sale in recent_sales],
            "low_stock_items": low_stock_items[:10],
        }

        return success_response(
            "Dashboard fetched successfully.",
            {"dashboard": dashboard},
        )
    except Exception:
        return error_response("An internal server error occurred.", status=500)
