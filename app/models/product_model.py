from app.extensions import db
from app.utils import utc_now


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(100),nullable=True)
    quantity = db.Column(db.Integer,nullable=False)
    sku = db.Column(db.String(50),nullable=False,unique=True)

    def to_dict(self):
     
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "category":self.category,
            "quantity":self.quantity,
            "sku":self.sku,
        }