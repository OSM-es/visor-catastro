import os


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "flask secret key")
    CLIENT_URL = os.getenv("CLIENT_URL", "http://localhost:5173")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "gis")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{POSTGRES_USER}:"
        f"{POSTGRES_PASSWORD}@postgres/{POSTGRES_DB}"
    )
