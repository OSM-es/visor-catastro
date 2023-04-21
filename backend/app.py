from flask import Flask

def create_uploader():
    uploader_app = Flask('uploader')

    from uploader import uploader
    uploader_app.register_blueprint(uploader)

    return uploader_app

def create_app():
    app = Flask(__name__)

    from api import api
    app.register_blueprint(api)

    return app
