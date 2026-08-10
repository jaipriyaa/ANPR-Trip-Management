from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class VehicleDetectionBase(BaseModel):
    plate_text: str = Field(..., max_length=20)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    is_valid_plate: bool = False
    upload_type: str = Field("image", pattern="^(image|video)$")
    uploaded_file_path: str
    cropped_vehicle_path: Optional[str] = None
    cropped_plate_path: Optional[str] = None
    source_filename: str
    detection_status: str = Field("pending", pattern="^(pending|processing|completed|failed)$")


class VehicleDetectionCreate(VehicleDetectionBase):
    vehicle_id: Optional[UUID] = None
    ai_model_version: Optional[str] = None
    processing_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    ocr_raw_text: Optional[str] = None
    detection_bbox: Optional[dict] = None
    vehicle_bbox: Optional[dict] = None
    frame_count: Optional[int] = None
    corrected_plate: Optional[str] = None
    vehicle_type_detected: Optional[str] = None
    validation_details: Optional[list] = None
    pipeline_metrics: Optional[dict] = None
    fusion_method: Optional[str] = None
    character_consistency: Optional[float] = None


class VehicleDetectionUpdate(BaseModel):
    vehicle_id: Optional[UUID] = None
    plate_text: Optional[str] = None
    confidence: Optional[float] = None
    is_valid_plate: Optional[bool] = None
    detection_status: Optional[str] = None
    cropped_vehicle_path: Optional[str] = None
    cropped_plate_path: Optional[str] = None
    ai_model_version: Optional[str] = None
    processing_time_ms: Optional[float] = None
    error_message: Optional[str] = None


class VehicleDetectionResponse(VehicleDetectionBase):
    id: UUID
    vehicle_id: Optional[UUID] = None
    ai_model_version: Optional[str] = None
    processing_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    ocr_raw_text: Optional[str] = None
    detection_bbox: Optional[dict] = None
    vehicle_bbox: Optional[dict] = None
    frame_count: Optional[int] = None
    corrected_plate: Optional[str] = None
    vehicle_type_detected: Optional[str] = None
    validation_details: Optional[list] = None
    pipeline_metrics: Optional[dict] = None
    fusion_method: Optional[str] = None
    character_consistency: Optional[float] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VehicleDetectionPaginatedResponse(BaseModel):
    total: int
    items: List[VehicleDetectionResponse]
