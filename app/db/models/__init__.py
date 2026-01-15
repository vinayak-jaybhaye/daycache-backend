from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import models -> Alembic can detect them
from .user import User
from .day import Day
from .entry import Entry
