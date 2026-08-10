import uuid
from sqlalchemy import Column, String, Integer, Float, Date, DateTime, func
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base


class DailySummary(Base):
    __tablename__ = "daily_summary"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    summary_date = Column(Date, nullable=False, unique=True, index=True)

    vehicles_entered = Column(Integer, nullable=False, default=0)
    vehicles_exited = Column(Integer, nullable=False, default=0)
    vehicles_still_inside = Column(Integer, nullable=False, default=0)

    trips_completed = Column(Integer, nullable=False, default=0)
    trips_cancelled = Column(Integer, nullable=False, default=0)

    late_arrivals = Column(Integer, nullable=False, default=0)
    overstay_cases = Column(Integer, nullable=False, default=0)
    unauthorized_attempts = Column(Integer, nullable=False, default=0)

    recognition_accuracy = Column(Float, nullable=False, default=99.2)
    avg_stay_duration_mins = Column(Float, nullable=False, default=45.0)
    avg_ocr_confidence = Column(Float, nullable=False, default=0.96)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
