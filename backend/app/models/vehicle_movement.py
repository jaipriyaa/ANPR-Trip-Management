import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class VehicleMovement(Base):
    __tablename__ = "vehicle_movements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
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
    recognized_plate = Column(String(50), nullable=False, index=True)

    entry_gate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("gates.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    exit_gate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("gates.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    entry_camera_id = Column(
        UUID(as_uuid=True),
        ForeignKey("gate_cameras.id", ondelete="SET NULL"),
        nullable=True
    )
    exit_camera_id = Column(
        UUID(as_uuid=True),
        ForeignKey("gate_cameras.id", ondelete="SET NULL"),
        nullable=True
    )

    entry_time = Column(DateTime(timezone=True), nullable=False, default=func.now(), index=True)
    exit_time = Column(DateTime(timezone=True), nullable=True, index=True)

    stay_duration_minutes = Column(Float, nullable=True)
    stay_duration_formatted = Column(String(100), nullable=True)

    movement_status = Column(String(20), nullable=False, default="INSIDE", index=True)  # INSIDE, OUTSIDE
    vehicle_status = Column(String(20), nullable=False, default="ENTERED", index=True)   # ENTERED, EXITED
    recognition_confidence = Column(Float, nullable=False, default=0.0)
    vehicle_type = Column(String(50), nullable=True, default="Vehicle")

    driver_id = Column(
        UUID(as_uuid=True),
        ForeignKey("drivers.id", ondelete="SET NULL"),
        nullable=True
    )
    transporter_id = Column(
        UUID(as_uuid=True),
        ForeignKey("transporters.id", ondelete="SET NULL"),
        nullable=True
    )

    purpose = Column(String(200), nullable=True)
    destination = Column(String(200), nullable=True)
    cropped_vehicle_path = Column(String(500), nullable=True)
    cropped_plate_path = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    vehicle = relationship("Vehicle", back_populates="movements")
    vehicle_plate = relationship("VehiclePlate")
    entry_gate = relationship("Gate", foreign_keys=[entry_gate_id])
    exit_gate = relationship("Gate", foreign_keys=[exit_gate_id])
    entry_camera = relationship("Camera", foreign_keys=[entry_camera_id])
    exit_camera = relationship("Camera", foreign_keys=[exit_camera_id])
    driver = relationship("Driver")
    transporter = relationship("Transporter")
