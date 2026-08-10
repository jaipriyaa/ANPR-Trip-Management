import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Float, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class GateRule(Base):
    __tablename__ = "gate_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    gate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("gates.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True
    )
    allow_entry = Column(Boolean, default=True, nullable=False)
    allow_exit = Column(Boolean, default=True, nullable=False)
    allow_trucks = Column(Boolean, default=True, nullable=False)
    allow_buses = Column(Boolean, default=True, nullable=False)
    allow_cars = Column(Boolean, default=True, nullable=False)
    allow_two_wheelers = Column(Boolean, default=False, nullable=False)
    maximum_vehicle_height = Column(Float, nullable=True, default=4.5)  # in meters
    maximum_vehicle_weight = Column(Float, nullable=True, default=40.0)  # in tons
    authorized_only = Column(Boolean, default=True, nullable=False)
    working_hours_start = Column(String(10), nullable=True, default="06:00")
    working_hours_end = Column(String(10), nullable=True, default="22:00")
    remarks = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    gate = relationship("Gate", back_populates="rule")
