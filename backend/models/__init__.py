from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.fixme import Fixme
from models.municipality import Municipality, MunicipalityUpdate
from models.province import Province
from models.user import OsmUser, User
from models.history import History, TaskHistory, TaskLock, StreetHistory, StreetLock
from models.street import Street
from models.task import Task, TaskUpdate
