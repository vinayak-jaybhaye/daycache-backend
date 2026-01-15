from sqlalchemy import (
    Column,
    BigInteger,
    TIMESTAMP,
    Text,
    ForeignKey,
    Index,
    func,
    Date,
)
from . import Base

class Entry(Base):
    __tablename__ = "entries"

    id = Column(BigInteger, primary_key=True)

    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    content = Column(Text, nullable=False)

    entry_date = Column(
        Date,
        nullable=False,
        index=True,
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

    __table_args__ = (
        Index("idx_entries_user_date", "user_id", "entry_date"),
    )
