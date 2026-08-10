from datetime import datetime
from typing import Optional, Any, Dict, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class OcrResultBase(BaseModel):
    trip_id: Optional[UUID] = None
    plate_text: str = Field(..., max_length=20)
    confidence: float = Field(..., ge=0.0, le=1.0)
    country: Optional[str] = Field(None, max_length=10)
    state: Optional[str] = Field(None, max_length=50)
    is_valid: bool = False
    correction_method: str = Field("RAW", max_length=20)
    source_frame_path: Optional[str] = None
    cropped_plate_path: Optional[str] = None
    raw_text: Optional[str] = None
    detection_bbox: Optional[Dict[str, Any]] = None
    processing_time_ms: Optional[float] = None


class OcrResultCreate(OcrResultBase):
    pass


class OcrResultInDBBase(OcrResultBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class OcrResultResponse(OcrResultInDBBase):
    pass


class OcrResultPaginatedResponse(BaseModel):
    total: int
    items: List[OcrResultResponse]
