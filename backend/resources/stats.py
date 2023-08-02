from flask_restful import Resource

import models


class Stats(Resource):
    def get(self, code=None):
        return {
            'buildings': models.Task.count_buildings(code),
            'addresses': models.Task.count_addresses(code),
            'users': models.User.query.count(),
            'mappers': models.Task.count_mappers(code),
        }
