import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class TripStatusHistory(Base):
    __tablename__ = "trip_status_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(
        UUID(as_uuid=True),
        ForeignKey("scheduled_trips.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    previous_status = Column(String(20), nullable=True)
    current_status = Column(String(20), nullable=False)
    changed_by = Column(String(100), nullable=False, default="SYSTEM_AI_ENGINE")
    changed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    remarks = Column(Text, nullable=True)

    # Relationships
    trip = relationship("ScheduledTrip", back_populates="status_history")
