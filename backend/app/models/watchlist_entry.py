import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.base import Base


class WatchlistEntry(Base):
    __tablename__ = "watchlist_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    plate_number = Column(String(50), nullable=False, index=True)
    reason = Column(String(255), nullable=False)  # Blacklisted, Expired Registration, Stolen Vehicle, Suspended Transporter, Security Alert
    severity = Column(String(20), nullable=False, default="HIGH")  # LOW, MEDIUM, HIGH, CRITICAL
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
