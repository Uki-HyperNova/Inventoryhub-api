from app.extensions import db
from app.utils import utc_now
from werkzeug.security import generate_password_hash, check_password_hash

class Auth(db.Model):
    __tablename__="Auth"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    def set_password(Self, password):
        Self.password = generate_password_hash(password)

    def check_password(Self, password):
        return check_password_hash(Self.password, password)

    def to_dict(self):
        return{
            "id":self.id,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,

        }