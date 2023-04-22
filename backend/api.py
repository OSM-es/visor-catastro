from flask import Blueprint, Response
import geopandas

from models import db, Task

api = Blueprint('api', __name__, url_prefix='/api')


@api.route("/<bounds>")
def upload(bounds):
    bounds = bounds.split(",")
    bb = f"LINESTRING({bounds[0]} {bounds[1]}, {bounds[2]} {bounds[3]})"
    sql = Task.query.filter(Task.geom.intersects(bb)).statement
    df = geopandas.GeoDataFrame.from_postgis(sql=sql, con=db.get_engine())
    return Response(df.to_json(), mimetype='application/json')
