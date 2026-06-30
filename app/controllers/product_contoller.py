from flask import jsonify, request 
from flask_jwt_extended import current_user
from app.utils import datetime

from app.extensions import db
from app.models.product_model import Product

def _validate_product_payload(data):
    errors = []
   
    if not data:
        return ["Request body is required."]

    
   
    if "name" in data:
        name = data.get("name")
        if name is None or str(name).strip() == "":
            errors.append("name cannot be empty.")
    

    
    if "price" in data:
        price = data.get("price")
        if price is None or str(price).strip() == "":
            errors.append("price cannot be empty.")
   


    if "quantity" in data:
        quantity = data.get("quantity")
        if quantity is None or int(quantity).strip() == "":
            errors.append("quantity cannot be empty.")


    
    if "category" in data:
        category = data.get("category")
        if category is None or int(category).strip() == "":
            errors.append("category cannot be empty.")
    

    if "sku" in data:
        sku = data.get("sku")
        if sku is None or int(sku).strip() == "":
            errors.append("sku cannot be empty.")
   
   
    

        
    return errors 

    
def get_all_products():
    try:
        products = Product.query.all()
        return jsonify({"products": [p.to_dict() for p in products]}), 200
    except Exception:
        return jsonify({"error": "An internal server error occurred."}), 500
           
def get_product(product_id):
    try:
        product = db.session.get(Product, product_id)
        if not product:
            return jsonify({"error": "Product not found."}), 404
        return jsonify({"product": product.to_dict()}), 200
    except Exception:
        return jsonify({"error": "An internal server error occurred."}), 500

def create_product():
    data = request.get_json(force=True)

    if not data:
        return jsonify({"error":"Request body is required/"})
    
    errors = _validate_product_payload(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    try:
        product =Product(
            name =data.get("name").strip(),
            price = float(data.get("price")),
            category = data.get("category"),
            quantity = data.get("quantity"),
            sku = data.get("sku")
        )
        pick =str(product)

        db.session.add(pick)
        db.session.commit()
        return jsonify({"message":"Product is created"})
    except Exception:
        db.session.rollback()
        return jsonify({"error":"An internal error occurred."})

    


def delete_product(product_id):
    try:
        product = db.session.get(Product, product_id)
        if not product:
            return jsonify({"error": "Product not found."}), 404
        
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully."}), 200
    except Exception:
        db.session.rollback()
        return jsonify({"error": "An internal server error occurred."}), 500
