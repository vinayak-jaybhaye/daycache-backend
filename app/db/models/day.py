from sqlalchemy import (
    Column,
    BigInteger,
    Date,
    Text,
    ForeignKey,
    TIMESTAMP,
    UniqueConstraint,
    Index,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import String
from . import Base

class Day(Base):
    __tablename__ = "days"

    id = Column(BigInteger, primary_key=True)

    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    date = Column(Date, nullable=False)

    summary = Column(Text, nullable=True)
    tags = Column(ARRAY(String), nullable=True)

    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        TIMESTAMP(timezone=True),
        onupdate=func.now(),
    )

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uq_days_user_date"),
        Index("ix_days_tags", tags, postgresql_using="gin"),
    )
