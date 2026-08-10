import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.base import Base


class WhitelistEntry(Base):
    __tablename__ = "whitelist_entries"

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
        nullable=True
    )
    transporter_id = Column(
        UUID(as_uuid=True),
        ForeignKey("transporters.id", ondelete="SET NULL"),
        nullable=True
    )
    driver_id = Column(
        UUID(as_uuid=True),
        ForeignKey("drivers.id", ondelete="SET NULL"),
        nullable=True
    )

    recognized_plate = Column(String(50), nullable=False, index=True)
    authorized_from = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    authorized_to = Column(DateTime(timezone=True), nullable=True)
    allowed_entry_gates = Column(String(255), nullable=True, default="ALL")
    allowed_exit_gates = Column(String(255), nullable=True, default="ALL")
    allowed_days = Column(String(255), nullable=True, default="MON,TUE,WED,THU,FRI,SAT,SUN")
    allowed_start_time = Column(String(10), nullable=True, default="00:00")
    allowed_end_time = Column(String(10), nullable=True, default="23:59")
    status = Column(String(20), nullable=False, default="ACTIVE")  # ACTIVE, INACTIVE
    remarks = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    vehicle = relationship("Vehicle")
    driver = relationship("Driver")
    transporter = relationship("Transporter")
