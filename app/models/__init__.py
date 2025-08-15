from sqlalchemy.orm import declarative_base

Base = declarative_base()

from .user import User
from .day import Day
from .entry import Entry
from .media import Media