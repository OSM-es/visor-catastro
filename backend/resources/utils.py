import gzip
from functools import wraps

from flask import Response


def json_compress(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = f(args[0])
        content = gzip.compress(data)
        response = Response(content, mimetype='application/json')
        response.headers['Content-length'] = len(content)
        response.headers['Content-Encoding'] = 'gzip'
        return response
    return decorated_function


