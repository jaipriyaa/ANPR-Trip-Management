import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class ScheduledTrip(Base):
    __tablename__ = "scheduled_trips"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_number = Column(String(50), nullable=False, unique=True, index=True)

    vehicle_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    vehicle_plate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vehicle_plates.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    driver_id = Column(
        UUID(as_uuid=True),
        ForeignKey("drivers.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    transporter_id = Column(
        UUID(as_uuid=True),
        ForeignKey("transporters.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    entry_gate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("gates.id", ondelete="SET NULL"),
        nullable=True
    )
    exit_gate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("gates.id", ondelete="SET NULL"),
        nullable=True
    )

    expected_entry_time = Column(DateTime(timezone=True), nullable=False, index=True)
    expected_exit_time = Column(DateTime(timezone=True), nullable=False, index=True)
    actual_entry_time = Column(DateTime(timezone=True), nullable=True)
    actual_exit_time = Column(DateTime(timezone=True), nullable=True)

    purpose = Column(String(200), nullable=False, default="Material Delivery")
    material_name = Column(String(100), nullable=True)
    material_quantity = Column(String(50), nullable=True)
    source_location = Column(String(150), nullable=True)
    destination_location = Column(String(150), nullable=True)
    priority = Column(String(20), nullable=False, default="MEDIUM")  # LOW, MEDIUM, HIGH, URGENT

    # Trip Status: SCHEDULED, WAITING, INSIDE, COMPLETED, CANCELLED
    trip_status = Column(String(20), nullable=False, default="SCHEDULED", index=True)
    # Approval Status: PENDING, APPROVED, REJECTED
    approval_status = Column(String(20), nullable=False, default="PENDING", index=True)

    remarks = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    vehicle = relationship("Vehicle", back_populates="trips")
    vehicle_plate = relationship("VehiclePlate")
    driver = relationship("Driver", back_populates="scheduled_trips")
    transporter = relationship("Transporter")
    entry_gate = relationship("Gate", foreign_keys=[entry_gate_id])
    exit_gate = relationship("Gate", foreign_keys=[exit_gate_id])
    status_history = relationship("TripStatusHistory", back_populates="trip", cascade="all, delete-orphan", order_by="TripStatusHistory.changed_at.desc()")
