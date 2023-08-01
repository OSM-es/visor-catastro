from sqlalchemy import func
from flask_restful import Resource

import models


class Stats(Resource):
    def get(self):
        return {
            'buildings': models.Task.count_buildings(),
            'addresses': models.Task.count_addresses(),
            'users': models.User.query.count(),
            'mappers': models.Task.count_mappers(),
        }
