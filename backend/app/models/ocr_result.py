import uuid
from sqlalchemy import Column, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class OcrResult(Base):
    __tablename__ = "ocr_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(
        UUID(as_uuid=True),
        ForeignKey("trips.id", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    plate_text = Column(String(20), nullable=False, index=True)
    confidence = Column(Float, nullable=False, default=0.0)
    country = Column(String(10), nullable=True)
    state = Column(String(50), nullable=True)
    is_valid = Column(Boolean, default=False, nullable=False)
    correction_method = Column(String(20), nullable=False, default="RAW")
    source_frame_path = Column(String(500), nullable=True)
    cropped_plate_path = Column(String(500), nullable=True)
    raw_text = Column(String(20), nullable=True)
    detection_bbox = Column(JSONB, nullable=True)
    processing_time_ms = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    trip = relationship("Trip", back_populates="ocr_results")
