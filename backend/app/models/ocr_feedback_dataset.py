import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, func
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base


class OcrFeedbackDataset(Base):
    __tablename__ = "ocr_feedback_dataset"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    manual_review_id = Column(
        UUID(as_uuid=True),
        ForeignKey("manual_reviews.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    raw_ocr_text = Column(String(100), nullable=False)
    corrected_ocr_text = Column(String(100), nullable=False, index=True)
    confidence = Column(Float, nullable=False, default=0.65)

    vehicle_image_path = Column(String(255), nullable=True)
    plate_image_path = Column(String(255), nullable=True)

    reviewer = Column(String(100), nullable=False, default="Security Officer")
    correction_source = Column(String(50), nullable=False, default="MANUAL_REVIEW_QUEUE")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
