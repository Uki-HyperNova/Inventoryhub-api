import os
import logging

from flask_cors import CORS

from app import create_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app()
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

with app.app_context():
    from app.extensions import db
    try:
        db.create_all()
    except Exception:
        # Don't let a slow-to-start or momentarily unreachable database take
        # the whole web process down at boot. Requests will still hit the
        # OperationalError handler in app/__init__.py and return a clean
        # 503/500 instead of the deploy failing its health check.
        logger.exception("Could not create database tables at startup.")

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
