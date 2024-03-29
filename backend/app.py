from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

from config import Config
from models import db


def create_uploader():
    uploader_app = Flask('uploader')
    uploader_app.config.from_object(Config)
    db.init_app(uploader_app)
    Migrate(uploader_app, db)

    from uploader import uploader
    uploader_app.register_blueprint(uploader)

    return uploader_app

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    origins = '*' if app.config.get('DEBUG', False) else app.config['CLIENT_URL']
    CORS(app, resources={r'/*': {'origins': origins}}, supports_credentials=True)
    db.init_app(app)
    Migrate(app, db)

    from auth import auth_bp
    app.register_blueprint(auth_bp)
    from api import api_bp, api_cache
    api_cache.init_app(app)
    app.register_blueprint(api_bp)

    return app
