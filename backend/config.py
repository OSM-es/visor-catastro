import os
from logging.config import dictConfig

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(levelname)s] %(message)s",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
                "formatter": "default",
            }
        },
        "root": {"level": "INFO", "handlers": ["console"]},
    }
)

class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "flask secret key")
    CLIENT_URL = os.getenv("CLIENT_URL", "http://127.0.0.1:5173")
    POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "gis")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql://{POSTGRES_USER}:"
        f"{POSTGRES_PASSWORD}@postgres/{POSTGRES_DB}"
    )
    OSM_CLIENT_ID = os.getenv("OSM_CLIENT_ID", "")
    OSM_CLIENT_SECRET = os.getenv("OSM_CLIENT_SECRET", "")
    OSM_URL = os.getenv("OSM_URL", "https://www.openstreetmap.org")
