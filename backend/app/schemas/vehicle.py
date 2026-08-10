from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.transporter import TransporterResponse
from app.schemas.vehicle_plate import VehiclePlateResponse
from app.schemas.vehicle_detection import VehicleDetectionResponse


class VehicleBase(BaseModel):
    vehicle_number: str = Field(..., max_length=20, description="Primary Vehicle Registration Number")
    vehicle_type: str = Field("Truck", max_length=50, description="Vehicle Category: Truck, Tanker, Trailer, LCV, Car")
    make_model: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=50)
    capacity_tons: Optional[Decimal] = Field(None, ge=0, le=1000)
    transporter_id: Optional[UUID] = None
    is_active: bool = True
    is_blacklisted: bool = False


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    vehicle_number: Optional[str] = Field(None, max_length=20)
    vehicle_type: Optional[str] = Field(None, max_length=50)
    make_model: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=50)
    capacity_tons: Optional[Decimal] = Field(None, ge=0, le=1000)
    transporter_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    is_blacklisted: Optional[bool] = None


class VehicleInDBBase(VehicleBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VehicleResponse(VehicleInDBBase):
    transporter: Optional[TransporterResponse] = None
    plates: List[VehiclePlateResponse] = []


class VehicleRecognitionResponse(VehicleInDBBase):
    first_seen_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    visit_count: int = 0
    detection_count: int = 0
    last_ocr_confidence: Optional[float] = None
    cropped_vehicle_image_path: Optional[str] = None
    cropped_plate_image_path: Optional[str] = None
    transporter: Optional[TransporterResponse] = None
    plates: List[VehiclePlateResponse] = []
    detections: List[VehicleDetectionResponse] = []


class VehiclePaginatedResponse(BaseModel):
    total: int
    items: List[VehicleResponse]


class VehicleRecognitionPaginatedResponse(BaseModel):
    total: int
    items: List[VehicleRecognitionResponse]