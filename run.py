import os
from flask_cors import CORS

from app import create_app

app = create_app()
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

with app.app_context ():
    from app.extensions import db
    db.create_all()

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )
