import uuid
from sqlalchemy import Column, String, Boolean, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class VehiclePlate(Base):
    __tablename__ = "vehicle_plates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    plate_number = Column(String(20), nullable=False, index=True)
    plate_type = Column(String(30), nullable=False, default="Standard")  # Standard, Commercial, High Security, Foreign
    is_primary = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    valid_from = Column(Date, nullable=True)
    valid_to = Column(Date, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationship
    vehicle = relationship("Vehicle", back_populates="plates")