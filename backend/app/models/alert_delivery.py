import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base


class AlertDelivery(Base):
    __tablename__ = "alert_deliveries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_id = Column(UUID(as_uuid=True), ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False, index=True)
    channel = Column(String(50), nullable=False, default="DASHBOARD")  # DASHBOARD, EMAIL, WEBHOOK
    status = Column(String(20), nullable=False, default="PENDING", index=True)  # PENDING, SENT, DELIVERED, FAILED
    attempt_count = Column(Integer, nullable=False, default=1)
    
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    failure_reason = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
