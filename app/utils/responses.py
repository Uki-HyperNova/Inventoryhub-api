from flask import jsonify


def success_response(message: str = "", data=None, status: int = 200):
    payload: dict = {"success": True, "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status


def error_response(
    message: str = "",
    errors=None,
    status: int = 400,
):
    payload: dict = {"success": False, "message": message}
    if errors is not None:
        payload["errors"] = errors
    return jsonify(payload), status
