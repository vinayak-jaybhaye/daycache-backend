from sqlalchemy import Column, BigInteger, TIMESTAMP, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timezone

class Day(Base):
    __tablename__ = "days"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    latest_summary = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="days")
    entries = relationship("Entry", back_populates="day", cascade="all, delete")
