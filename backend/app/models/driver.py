import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Driver(Base):
    __tablename__ = "drivers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transporter_id = Column(
        UUID(as_uuid=True),
        ForeignKey("transporters.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    full_name = Column(String(150), nullable=False, index=True)
    license_number = Column(String(50), nullable=False, unique=True, index=True)
    phone_number = Column(String(20), nullable=False)
    identity_card_no = Column(String(50), nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    transporter = relationship("Transporter", back_populates="drivers")
    scheduled_trips = relationship("ScheduledTrip", back_populates="driver")
