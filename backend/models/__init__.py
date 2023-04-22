from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.task import Task
from models.municipality import Municipality