from flask import Blueprint

api = Blueprint('api', __name__, url_prefix='/api')

@api.route("/<bounds>")
def upload(bounds):
    return f"api {bounds}!"
