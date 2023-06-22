from flask_restful import Resource

from resources.municipalities import Municipalities
from resources.provinces import Provinces
from resources.user import User
from resources.streets import Streets, Street
from resources.tasks import Tasks, Task


class Status(Resource):
    def get(self):
        return 'OK'
