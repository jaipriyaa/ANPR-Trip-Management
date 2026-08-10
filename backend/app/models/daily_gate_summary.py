import uuid
from sqlalchemy import Column, String, Integer, Float, Date, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base


class DailyGateSummary(Base):
    __tablename__ = "daily_gate_summary"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    summary_date = Column(Date, nullable=False, index=True)
    gate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("gates.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    gate_name = Column(String(100), nullable=False)

    vehicles_entered = Column(Integer, nullable=False, default=0)
    vehicles_exited = Column(Integer, nullable=False, default=0)

    avg_processing_time_secs = Column(Float, nullable=False, default=1.2)
    avg_stay_duration_mins = Column(Float, nullable=False, default=42.5)

    alerts_generated = Column(Integer, nullable=False, default=0)
    recognition_accuracy = Column(Float, nullable=False, default=99.4)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
