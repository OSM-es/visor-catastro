from flask import Blueprint

uploader = Blueprint('uploader', __name__, url_prefix='/')

@uploader.route("/<mun_code>")
def upload(mun_code):
    print(f"uploading {mun_code}!")
    return f"uploading {mun_code}!"
