from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class TripBase(BaseModel):
    plate_number: str = Field(..., max_length=20)
    entry_time: datetime
    exit_time: Optional[datetime] = None
    purpose: Optional[str] = Field(None, max_length=200)
    destination: Optional[str] = Field(None, max_length=200)
    expected_exit_time: Optional[datetime] = None
    status: str = Field("ACTIVE", max_length=20)
    is_authorized: bool = False
    notes: Optional[str] = None
    vehicle_id: Optional[UUID] = None
    driver_id: Optional[UUID] = None
    gate_id: Optional[UUID] = None
    authorization_id: Optional[UUID] = None


class TripCreate(TripBase):
    pass


class TripUpdate(BaseModel):
    exit_time: Optional[datetime] = None
    status: Optional[str] = Field(None, max_length=20)
    purpose: Optional[str] = Field(None, max_length=200)
    destination: Optional[str] = Field(None, max_length=200)
    expected_exit_time: Optional[datetime] = None
    is_authorized: Optional[bool] = None
    notes: Optional[str] = None
    driver_id: Optional[UUID] = None
    authorization_id: Optional[UUID] = None


class TripExitUpdate(BaseModel):
    exit_time: datetime
    status: str = Field("COMPLETED", max_length=20)


class TripInDBBase(TripBase):
    id: UUID
    stay_duration_seconds: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TripResponse(TripInDBBase):
    vehicle_number: Optional[str] = None
    driver_name: Optional[str] = None
    gate_name: Optional[str] = None
    event_count: Optional[int] = None


class TripPaginatedResponse(BaseModel):
    total: int
    items: List[TripResponse]
