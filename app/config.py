from datetime import timedelta
import os

from dotenv import load_dotenv

load_dotenv()


def _build_database_uri():
    # Railway's MySQL plugin exposes a ready-made connection string here.
    # If it's present, use it directly (just swap the driver prefix so
    # SQLAlchemy uses PyMySQL instead of the default mysql:// dialect).
    railway_url = os.getenv("MYSQL_URL") or os.getenv("MYSQL_PUBLIC_URL")
    if railway_url:
        if railway_url.startswith("mysql://"):
            railway_url = railway_url.replace("mysql://", "mysql+pymysql://", 1)
        return railway_url

    # Otherwise, fall back to individual pieces. Support both Railway's
    # variable names (MYSQLHOST, MYSQLUSER, ...) and this project's original
    # DB_* names, so the same code works locally and on Railway.
    db_user = os.getenv("MYSQLUSER") or os.getenv("DB_USER", "root")
    db_password = os.getenv("MYSQLPASSWORD") or os.getenv("DB_PASSWORD", "root123")
    db_host = os.getenv("MYSQLHOST") or os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("MYSQLPORT") or os.getenv("DB_PORT", "3306")
    db_name = os.getenv("MYSQLDATABASE") or os.getenv("DB_NAME", "inventoryhub_db")

    return f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


class Config:
    SQLALCHEMY_DATABASE_URI = _build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        # Railway's MySQL proxy can drop idle connections; recycling and
        # pre-pinging avoids "MySQL server has gone away" errors.
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-me")
    # Flask-JWT-Extended reads JWT_ACCESS_TOKEN_EXPIRES specifically — the
    # previous JWT_TIMEOUT key was never read by the library, so tokens
    # silently never expired.
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("JWT_TIMEOUT", "15"))
    )
