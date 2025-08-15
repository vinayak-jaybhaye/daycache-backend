from sqlalchemy import Column, BigInteger, TIMESTAMP, VARCHAR, Text, ARRAY, ForeignKey
from sqlalchemy.orm import relationship
from . import Base
from datetime import datetime, timezone


class Entry(Base):
    __tablename__ = "entries"

    id = Column(BigInteger, primary_key=True, index=True)
    day_id = Column( BigInteger, ForeignKey("days.id", ondelete="CASCADE"), nullable=False )
    location = Column(VARCHAR(200), nullable=True)
    content = Column(Text, nullable=True)
    tags = Column(ARRAY(VARCHAR), nullable=True)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))

    day = relationship("Day", back_populates="entries")
    media = relationship("Media", back_populates="entry", cascade="all, delete")
