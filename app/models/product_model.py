from app.extensions import db


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    sku = db.Column(db.String(50), nullable=False, unique=True, index=True)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    category = db.Column(db.String(100), nullable=False)
    low_stock_threshold = db.Column(db.Integer, nullable=False, default=10)

    sale_items = db.relationship("SaleItem", backref="product", lazy="dynamic")

    def is_low_stock(self) -> bool:
        return self.quantity <= self.low_stock_threshold

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "sku": self.sku,
            "price": self.price,
            "quantity": self.quantity,
            "category": self.category,
            "low_stock_threshold": self.low_stock_threshold,
        }
