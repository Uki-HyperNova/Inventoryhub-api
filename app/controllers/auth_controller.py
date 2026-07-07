from flask import jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from email_validator import EmailNotValidError, validate_email
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.user_model import User
from app.utils.responses import error_response, success_response


def _validate_register_payload(data: dict | None) -> dict[str, list[str]]:
    errors: dict[str, list[str]] = {}

    if not data:
        return {"_schema": ["Request body is required."]}

    name = data.get("name")
    if name is None or str(name).strip() == "":
        errors.setdefault("name", []).append("Name is required.")
    else:
        name_str = str(name).strip()
        if len(name_str) < 3:
            errors.setdefault("name", []).append("Name must be at least 3 characters.")
        elif len(name_str) > 100:
            errors.setdefault("name", []).append("Name must not exceed 100 characters.")

    email = data.get("email")
    if email is None or str(email).strip() == "":
        errors.setdefault("email", []).append("Email is required.")
    else:
        try:
            validate_email(str(email).strip(), check_deliverability=False)
        except EmailNotValidError:
            errors.setdefault("email", []).append("Invalid email.")

    password = data.get("password")
    if password is None or str(password) == "":
        errors.setdefault("password", []).append("Password is required.")
    else:
        password_str = str(password)
        if len(password_str) < 8:
            errors.setdefault("password", []).append(
                "Password must be at least 8 characters."
            )
        elif len(password_str) > 100:
            errors.setdefault("password", []).append(
                "Password must not exceed 100 characters."
            )

    confirm_password = data.get("confirm_password")
    if confirm_password is not None and str(confirm_password) != "":
        if password is not None and str(confirm_password) != str(password):
            errors.setdefault("confirm_password", []).append("Passwords do not match.")

    return errors


def _validate_login_payload(data: dict | None) -> dict[str, list[str]]:
    errors: dict[str, list[str]] = {}

    if not data:
        return {"_schema": ["Request body is required."]}

    email = data.get("email")
    if email is None or str(email).strip() == "":
        errors.setdefault("email", []).append("Email is required.")

    password = data.get("password")
    if password is None or str(password).strip() == "":
        errors.setdefault("password", []).append("Password is required.")

    return errors


def register():
    data = request.get_json(silent=True)
    errors = _validate_register_payload(data)

    if errors:
        return error_response("Validation failed.", errors, 400)

    email_str = str(data.get("email")).strip()
    try:
        email_info = validate_email(email_str, check_deliverability=False)
        normalized_email = email_info.normalized
    except EmailNotValidError:
        return error_response(
            "Validation failed.",
            {"email": ["Invalid email."]},
            400,
        )

    if User.query.filter_by(email=normalized_email).first():
        return error_response("Email already registered.", status=409)

    try:
        user = User(
            name=str(data.get("name")).strip(),
            email=normalized_email,
            role="staff",
        )
        user.set_password(str(data.get("password")))

        db.session.add(user)
        db.session.commit()

        return success_response(
            "Staff account created successfully.",
            user.to_dict(),
            201,
        )
    except IntegrityError:
        db.session.rollback()
        return error_response("Email already registered.", status=409)
    except Exception:
        db.session.rollback()
        return error_response("An internal server error occurred.", status=500)


def login():
    data = request.get_json(silent=True)
    errors = _validate_login_payload(data)
    if errors:
        return error_response("Validation failed.", errors, 400)

    try:
        email_str = str(data.get("email")).strip()
        try:
            email_info = validate_email(email_str, check_deliverability=False)
            email_str = email_info.normalized
        except EmailNotValidError:
            return error_response("Invalid email or password.", status=401)

        user = User.query.filter_by(email=email_str).first()

        if not user or not user.check_password(str(data.get("password"))):
            return error_response("Invalid email or password.", status=401)

        access_token = create_access_token(identity=str(user.id))
        return success_response(
            "Login successful.",
            {
                "access_token": access_token,
                "user": user.to_dict(),
            },
        )
    except Exception:
        return error_response("An internal server error occurred.", status=500)


@jwt_required()
def get_me():
    try:
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)
        if not user:
            return error_response("User not found.", status=404)
        return success_response("User fetched successfully.", user.to_dict())
    except Exception:
        return error_response("An internal server error occurred.", status=500)
