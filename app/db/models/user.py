from sqlalchemy import (
    Column,
    BigInteger,
    String,
    TIMESTAMP,
    func,
)
from . import Base

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True)

    email = Column(
        String(255),
        nullable=False,
        unique=True,
        index=True,   # important for lookup
    )

    password_hash = Column(
        String(255),
        nullable=True,
    )

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        TIMESTAMP(timezone=True),
        onupdate=func.now(),
    )