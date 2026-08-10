from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class VehicleMovementBase(BaseModel):
    recognized_plate: str = Field(..., max_length=50)
    vehicle_id: Optional[UUID] = None
    vehicle_plate_id: Optional[UUID] = None
    entry_gate_id: Optional[UUID] = None
    exit_gate_id: Optional[UUID] = None
    entry_camera_id: Optional[UUID] = None
    exit_camera_id: Optional[UUID] = None
    entry_time: datetime
    exit_time: Optional[datetime] = None
    stay_duration_minutes: Optional[float] = None
    stay_duration_formatted: Optional[str] = None
    movement_status: str = Field("INSIDE", max_length=20)  # INSIDE, OUTSIDE
    vehicle_status: str = Field("ENTERED", max_length=20)   # ENTERED, EXITED
    recognition_confidence: float = Field(0.0, ge=0.0, le=1.0)
    vehicle_type: Optional[str] = Field("Vehicle", max_length=50)
    driver_id: Optional[UUID] = None
    transporter_id: Optional[UUID] = None
    purpose: Optional[str] = None
    destination: Optional[str] = None
    cropped_vehicle_path: Optional[str] = None
    cropped_plate_path: Optional[str] = None


class VehicleMovementCreate(VehicleMovementBase):
    pass


class VehicleMovementUpdate(BaseModel):
    exit_gate_id: Optional[UUID] = None
    exit_camera_id: Optional[UUID] = None
    exit_time: Optional[datetime] = None
    stay_duration_minutes: Optional[float] = None
    stay_duration_formatted: Optional[str] = None
    movement_status: Optional[str] = None
    vehicle_status: Optional[str] = None
    recognition_confidence: Optional[float] = None
    purpose: Optional[str] = None
    destination: Optional[str] = None
    cropped_vehicle_path: Optional[str] = None
    cropped_plate_path: Optional[str] = None


class VehicleMovementInDBBase(VehicleMovementBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class VehicleMovementResponse(VehicleMovementInDBBase):
    entry_gate_code: Optional[str] = None
    entry_gate_name: Optional[str] = None
    exit_gate_code: Optional[str] = None
    exit_gate_name: Optional[str] = None
    driver_name: Optional[str] = None
    transporter_name: Optional[str] = None
    make_model: Optional[str] = None
    color: Optional[str] = None


class VehicleMovementPaginatedResponse(BaseModel):
    total: int
    items: List[VehicleMovementResponse]


class LiveMovementsSummaryResponse(BaseModel):
    vehicles_currently_inside: int
    vehicles_entered_today: int
    vehicles_exited_today: int
    avg_stay_duration_formatted: str
