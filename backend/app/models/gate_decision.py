import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.base import Base


class GateDecision(Base):
    __tablename__ = "gate_decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    tracking_id = Column(String(50), nullable=True)
    trip_id = Column(
        UUID(as_uuid=True),
        ForeignKey("scheduled_trips.id", ondelete="SET NULL"),
        nullable=True
    )
    gate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("gates.id", ondelete="SET NULL"),
        nullable=True
    )
    camera_id = Column(
        UUID(as_uuid=True),
        ForeignKey("gate_cameras.id", ondelete="SET NULL"),
        nullable=True
    )

    decision = Column(String(30), nullable=False, default="DENY")  # ALLOW, DENY, MANUAL_APPROVAL, MANUAL_REJECTION, PENDING_REVIEW
    reason = Column(String(255), nullable=False)
    recognized_plate = Column(String(50), nullable=False, index=True)
    confidence = Column(Float, nullable=False, default=0.95)
    decision_by = Column(String(100), nullable=False, default="Automated AI Gate Decision Engine")
    decision_time = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    vehicle = relationship("Vehicle")
    scheduled_trip = relationship("ScheduledTrip")
    gate = relationship("Gate")
    camera = relationship("Camera")
