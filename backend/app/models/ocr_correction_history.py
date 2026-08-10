import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.base import Base


class OcrCorrectionHistory(Base):
    __tablename__ = "ocr_correction_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    manual_review_id = Column(
        UUID(as_uuid=True),
        ForeignKey("manual_reviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    old_plate = Column(String(50), nullable=False)
    new_plate = Column(String(50), nullable=False)
    old_confidence = Column(Float, nullable=False, default=0.65)
    new_confidence = Column(Float, nullable=False, default=1.0)
    correction_reason = Column(String(255), nullable=True)
    reviewed_by = Column(String(100), nullable=False, default="Security Officer")
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    manual_review = relationship("ManualReview", back_populates="corrections_history")
