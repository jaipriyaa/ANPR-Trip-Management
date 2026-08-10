import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_key = Column(String(255), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False, index=True)  # LATE_ARRIVAL, OVERSTAY, UNAUTHORIZED_VEHICLE, etc.
    severity = Column(String(20), nullable=False, default="WARNING")  # INFO, WARNING, CRITICAL
    status = Column(String(20), nullable=False, default="OPEN", index=True)  # OPEN, ACKNOWLEDGED, RESOLVED, DISMISSED

    trip_id = Column(UUID(as_uuid=True), ForeignKey("scheduled_trips.id", ondelete="SET NULL"), nullable=True, index=True)
    movement_id = Column(UUID(as_uuid=True), ForeignKey("vehicle_movements.id", ondelete="SET NULL"), nullable=True, index=True)
    gate_id = Column(UUID(as_uuid=True), ForeignKey("gates.id", ondelete="SET NULL"), nullable=True, index=True)
    camera_id = Column(UUID(as_uuid=True), ForeignKey("gate_cameras.id", ondelete="SET NULL"), nullable=True, index=True)

    plate_number = Column(String(50), nullable=True, index=True)
    vehicle_type = Column(String(50), nullable=True)
    message = Column(String(500), nullable=True)
    reason = Column(String(500), nullable=True)
    metadata_json = Column(Text, nullable=True)

    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_reason = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
