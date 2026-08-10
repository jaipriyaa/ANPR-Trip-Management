import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class TripEvent(Base):
    __tablename__ = "trip_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(
        UUID(as_uuid=True),
        ForeignKey("trips.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    event_type = Column(String(30), nullable=False, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    description = Column(Text, nullable=True)
    event_metadata = Column("metadata", JSONB, nullable=True)

    trip = relationship("Trip", back_populates="events")
