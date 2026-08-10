import uuid
from sqlalchemy import Column, String, Boolean, Integer, Float, DateTime, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transporter_id = Column(
        UUID(as_uuid=True),
        ForeignKey("transporters.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    vehicle_number = Column(String(20), nullable=False, unique=True, index=True)
    vehicle_type = Column(String(50), nullable=False, default="Truck")  # Truck, Tanker, Trailer, LCV, Car
    make_model = Column(String(100), nullable=True)
    color = Column(String(50), nullable=True)
    capacity_tons = Column(Numeric(10, 2), nullable=True)
    
    is_active = Column(Boolean, default=True, nullable=False)
    is_blacklisted = Column(Boolean, default=False, nullable=False)

    # AI recognition tracking
    first_seen_at = Column(DateTime(timezone=True), nullable=True)
    last_seen_at = Column(DateTime(timezone=True), nullable=True)
    visit_count = Column(Integer, default=0, server_default="0", nullable=False)
    detection_count = Column(Integer, default=0, server_default="0", nullable=False)
    last_ocr_confidence = Column(Float, nullable=True)
    cropped_vehicle_image_path = Column(String(500), nullable=True)
    cropped_plate_image_path = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    transporter = relationship("Transporter", back_populates="vehicles")
    plates = relationship("VehiclePlate", back_populates="vehicle", cascade="all, delete-orphan")
    trips = relationship("ScheduledTrip", back_populates="vehicle")
    detections = relationship("VehicleDetection", back_populates="vehicle", cascade="all, delete-orphan")
    movements = relationship("VehicleMovement", back_populates="vehicle")