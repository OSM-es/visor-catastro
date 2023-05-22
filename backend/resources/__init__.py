from flask_restful import Resource

from resources.tasks import Tasks, Task
from resources.user import User


class Status(Resource):
    def get(self):
        return 'OK'
