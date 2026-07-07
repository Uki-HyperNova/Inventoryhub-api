import os
import time
import logging
from urllib.parse import urlsplit

from flask_cors import CORS

from app import create_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app()
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

with app.app_context():
    from app.extensions import db

    # Log which host:port we're actually trying to reach (no credentials)
    # so a misconfigured DB env var is obvious in the deploy logs instead of
    # a bare timeout.
    uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    parsed = urlsplit(uri)
    logger.info(
        "Connecting to database at %s:%s (db=%s)",
        parsed.hostname, parsed.port, (parsed.path or "").lstrip("/"),
    )

    max_attempts = 5
    for attempt in range(1, max_attempts + 1):
        try:
            db.create_all()
            logger.info("Database tables ready.")
            break
        except Exception:
            if attempt == max_attempts:
                # Don't let a database that's still unreachable after
                # several tries take the whole web process down. Requests
                # will still hit the OperationalError handler in
                # app/__init__.py and return a clean 503/500 instead of the
                # deploy crash-looping.
                logger.exception(
                    "Could not create database tables after %s attempts. "
                    "Check that SQLALCHEMY host/port above match your "
                    "database's private networking host (e.g. "
                    "mysql.railway.internal) or TCP proxy host+port from "
                    "the database's Connect tab — NOT its *.up.railway.app "
                    "domain, which only serves HTTP.",
                    max_attempts,
                )
            else:
                logger.warning(
                    "Database not reachable yet (attempt %s/%s), retrying in 3s...",
                    attempt, max_attempts,
                )
                time.sleep(3)

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
