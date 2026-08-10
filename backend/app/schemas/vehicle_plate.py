from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class VehiclePlateBase(BaseModel):
    plate_number: str = Field(..., max_length=20, description="ANPR Plate Registration String (e.g., KA01AB1234)")
    plate_type: str = Field("Standard", max_length=30, description="Plate Type: Standard, Commercial, High Security, Foreign")
    is_primary: bool = True
    is_active: bool = True
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None


class VehiclePlateCreate(VehiclePlateBase):
    vehicle_id: UUID


class VehiclePlateUpdate(BaseModel):
    plate_number: Optional[str] = Field(None, max_length=20)
    plate_type: Optional[str] = Field(None, max_length=30)
    is_primary: Optional[bool] = None
    is_active: Optional[bool] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None


class VehiclePlateInDBBase(VehiclePlateBase):
    id: UUID
    vehicle_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VehiclePlateResponse(VehiclePlateInDBBase):
    pass


class VehiclePlatePaginatedResponse(BaseModel):
    total: int
    items: List[VehiclePlateResponse]
