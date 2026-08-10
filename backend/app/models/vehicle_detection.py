import uuid
from sqlalchemy import Column, String, Boolean, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database.base import Base


class VehicleDetection(Base):
    __tablename__ = "vehicle_detections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_id = Column(
        UUID(as_uuid=True),
        ForeignKey("vehicles.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    plate_text = Column(String(20), nullable=False, index=True)
    confidence = Column(Float, nullable=False, default=0.0)
    is_valid_plate = Column(Boolean, default=False, nullable=False)

    upload_type = Column(String(10), nullable=False, default="image")
    uploaded_file_path = Column(String(500), nullable=False)
    cropped_vehicle_path = Column(String(500), nullable=True)
    cropped_plate_path = Column(String(500), nullable=True)
    source_filename = Column(String(255), nullable=False)

    ai_model_version = Column(String(50), nullable=True)
    processing_time_ms = Column(Float, nullable=True)
    detection_status = Column(String(20), nullable=False, default="pending")
    error_message = Column(Text, nullable=True)

    ocr_raw_text = Column(String(50), nullable=True)
    detection_bbox = Column(JSONB, nullable=True)
    vehicle_bbox = Column(JSONB, nullable=True)
    frame_count = Column(Integer, nullable=True)

    corrected_plate = Column(String(20), nullable=True)
    vehicle_type_detected = Column(String(50), nullable=True)
    validation_details = Column(JSONB, nullable=True)
    pipeline_metrics = Column(JSONB, nullable=True)
    fusion_method = Column(String(30), nullable=True)
    character_consistency = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    vehicle = relationship("Vehicle", back_populates="detections")
