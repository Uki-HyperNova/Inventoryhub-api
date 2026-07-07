from datetime import datetime,timezone
from flask import request

def utc_now():
    return datetime.now(timezone.utc)


def get_json_body():
    """Safely parse the request body as a JSON object.

    Returns the parsed dict, or None if the body is missing, isn't valid
    JSON, or is valid JSON that isn't an object (e.g. a bare string, number,
    or list) — which previously crashed controllers with an AttributeError
    when they called .get(...) on something that wasn't a dict.
    """
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return None
    return data
