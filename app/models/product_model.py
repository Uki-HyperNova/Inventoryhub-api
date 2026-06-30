from app.extensions import db
from app.utils import utc_now


class Product(db.Model):
    __tablename__ = "product"

    product_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    manufacture = db.Column(db.String(255), nullable=False)
    discription = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    def to_dict(self):
        """Return a dictionary representation of the product."""
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "manufacture": self.manufacture,
            "discription": self.discription,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }