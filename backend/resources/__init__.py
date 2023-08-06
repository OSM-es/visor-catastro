from flask_restful import Resource

from resources.fixme import Fixme
from resources.municipalities import Municipalities, Municipality
from resources.provinces import Provinces
from resources.user import User
from resources.stats import Stats, TasksStatus 
from resources.streets import Streets, Street, StreetLock
from resources.tasks import Tasks, Task


class Status(Resource):
    def get(self):
        return 'OK'
