from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


## what this does?
# This file contains the SQLAlchemy SessionLocal class and a get_db function.
# The SessionLocal class is a class provided by SQLAlchemy that represents a database session.
# The get_db function is a function that returns a new database session when called.
