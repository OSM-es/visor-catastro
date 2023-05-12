from flask_restful import Resource

from resources.tasks import Tasks


class Status(Resource):
    def get(self):
        return 'OK'
