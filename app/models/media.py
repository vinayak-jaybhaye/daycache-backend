from sqlalchemy import Column, BigInteger, TIMESTAMP, Text, VARCHAR, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timezone


class Media(Base):
    __tablename__ = "media"

    id = Column(BigInteger, primary_key=True, index=True)
    entry_id = Column(
        BigInteger, ForeignKey("entries.id", ondelete="CASCADE"), nullable=False
    )
    file_url = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=lambda: datetime.now(timezone.utc))

    entry = relationship("Entry", back_populates="media")
