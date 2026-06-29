import re
from flask import jsonify, request 
from flask_jwt_extended import create_access_token

from app.extensions import db
from app.models.auth_model import Auth

def _validate_register_payload(data):
    errors = []

def _validate_login_payload(data):
    errors = []
    if not data:
        return["Request body is required."]

    email = data.get("email")
    if email is None or str(email).strip() == "":
        errors.append("email is required.")

    password = data.get("password")
    if password is None or str(password).strip() == "":
        errors.append("password is required.")

    return errors

def register():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body is required."}), 400
    
    errors = _validate_register_payload(data)
    # if errors: