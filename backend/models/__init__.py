from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.municipality import Municipality
from models.user import OsmUser, User
from models.task import Task