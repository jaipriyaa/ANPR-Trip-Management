import uuid
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.base import Base


class ManualReview(Base):
    __tablename__ = "manual_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_detection_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vehicle_detections.id", ondelete="SET NULL"),
        nullable=True
    )
    vehicle_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    tracking_id = Column(String(50), nullable=True)

    recognized_plate = Column(String(50), nullable=False, index=True)
    corrected_plate = Column(String(50), nullable=True)
    raw_ocr_text = Column(String(100), nullable=True)
    confidence = Column(Float, nullable=False, default=0.65)
    vehicle_image_path = Column(String(255), nullable=True)
    plate_image_path = Column(String(255), nullable=True)

    review_status = Column(String(30), nullable=False, default="PENDING")  # PENDING, APPROVED, REJECTED, CORRECTED
    reviewed_by = Column(String(100), nullable=True)
    review_time = Column(DateTime(timezone=True), nullable=True)
    remarks = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    vehicle = relationship("Vehicle")
    corrections_history = relationship("OcrCorrectionHistory", back_populates="manual_review", cascade="all, delete-orphan")
