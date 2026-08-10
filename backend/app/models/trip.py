import uuid
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Trip(Base):
    __tablename__ = "trips"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    driver_id = Column(
        UUID(as_uuid=True),
        ForeignKey("drivers.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    gate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("gates.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    authorization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("authorizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    plate_number = Column(String(20), nullable=False, index=True)
    entry_time = Column(DateTime(timezone=True), nullable=False)
    exit_time = Column(DateTime(timezone=True), nullable=True)
    purpose = Column(String(200), nullable=True)
    destination = Column(String(200), nullable=True)
    expected_exit_time = Column(DateTime(timezone=True), nullable=True)
    stay_duration_seconds = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False, default="ACTIVE")
    is_authorized = Column(Boolean, default=False, nullable=False)
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    vehicle = relationship("Vehicle")
    driver = relationship("Driver")
    gate = relationship("Gate")
    authorization = relationship("Authorization", back_populates="trips")
    events = relationship("TripEvent", back_populates="trip", cascade="all, delete-orphan")
    ocr_results = relationship("OcrResult", back_populates="trip", cascade="all, delete-orphan")
