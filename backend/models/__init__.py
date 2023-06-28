from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.municipality import Municipality
from models.province import Province
from models.history import History, StreetHistory, TaskHistory
from models.user import OsmUser, User
from models.street import Street
from models.task import Task