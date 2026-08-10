from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class TripStatusHistoryResponse(BaseModel):
    id: UUID
    trip_id: UUID
    previous_status: Optional[str] = None
    current_status: str
    changed_by: str
    changed_at: datetime
    remarks: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class ScheduledTripBase(BaseModel):
    trip_number: Optional[str] = Field(None, max_length=50)
    vehicle_id: Optional[UUID] = None
    vehicle_plate_id: Optional[UUID] = None
    driver_id: Optional[UUID] = None
    transporter_id: Optional[UUID] = None
    entry_gate_id: Optional[UUID] = None
    exit_gate_id: Optional[UUID] = None
    expected_entry_time: datetime
    expected_exit_time: datetime
    actual_entry_time: Optional[datetime] = None
    actual_exit_time: Optional[datetime] = None
    purpose: str = Field("Material Delivery", max_length=200)
    material_name: Optional[str] = Field(None, max_length=100)
    material_quantity: Optional[str] = Field(None, max_length=50)
    source_location: Optional[str] = Field(None, max_length=150)
    destination_location: Optional[str] = Field(None, max_length=150)
    priority: str = Field("MEDIUM", max_length=20)  # LOW, MEDIUM, HIGH, URGENT
    trip_status: str = Field("SCHEDULED", max_length=20)  # SCHEDULED, WAITING, INSIDE, COMPLETED, CANCELLED
    approval_status: str = Field("PENDING", max_length=20)  # PENDING, APPROVED, REJECTED
    remarks: Optional[str] = None


class ScheduledTripCreate(ScheduledTripBase):
    recognized_plate: Optional[str] = None  # Helper for auto-resolving vehicle by plate


class ScheduledTripUpdate(BaseModel):
    driver_id: Optional[UUID] = None
    transporter_id: Optional[UUID] = None
    entry_gate_id: Optional[UUID] = None
    exit_gate_id: Optional[UUID] = None
    expected_entry_time: Optional[datetime] = None
    expected_exit_time: Optional[datetime] = None
    purpose: Optional[str] = None
    material_name: Optional[str] = None
    material_quantity: Optional[str] = None
    source_location: Optional[str] = None
    destination_location: Optional[str] = None
    priority: Optional[str] = None
    remarks: Optional[str] = None


class TripStatusUpdate(BaseModel):
    trip_status: str = Field(..., max_length=20)
    changed_by: str = Field("USER_OPERATOR", max_length=100)
    remarks: Optional[str] = None


class TripApprovalUpdate(BaseModel):
    approval_status: str = Field(..., max_length=20)  # APPROVED, REJECTED
    remarks: Optional[str] = None


class ScheduledTripInDBBase(ScheduledTripBase):
    id: UUID
    trip_number: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class ScheduledTripResponse(ScheduledTripInDBBase):
    vehicle_number: Optional[str] = None
    vehicle_type: Optional[str] = None
    driver_name: Optional[str] = None
    transporter_name: Optional[str] = None
    entry_gate_code: Optional[str] = None
    entry_gate_name: Optional[str] = None
    exit_gate_code: Optional[str] = None
    exit_gate_name: Optional[str] = None
    status_history: List[TripStatusHistoryResponse] = []


class ScheduledTripPaginatedResponse(BaseModel):
    total: int
    items: List[ScheduledTripResponse]


class TripDashboardSummaryResponse(BaseModel):
    active_trips: int
    completed_trips: int
    waiting_vehicles: int
    rejected_trips: int
    vehicles_inside: int
    todays_trips: int
    avg_trip_duration_formatted: str
