from datetime import timedelta
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:password@localhost/inventory_db",
    )

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "60"))
    )
