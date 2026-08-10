from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class GateRuleBase(BaseModel):
    allow_entry: bool = True
    allow_exit: bool = True
    allow_trucks: bool = True
    allow_buses: bool = True
    allow_cars: bool = True
    allow_two_wheelers: bool = False
    maximum_vehicle_height: Optional[float] = Field(4.5, ge=0.0, le=20.0)
    maximum_vehicle_weight: Optional[float] = Field(40.0, ge=0.0, le=200.0)
    authorized_only: bool = True
    working_hours_start: Optional[str] = Field("06:00", max_length=10)
    working_hours_end: Optional[str] = Field("22:00", max_length=10)
    remarks: Optional[str] = None
    is_active: bool = True


class GateRuleCreate(GateRuleBase):
    gate_id: UUID


class GateRuleUpdate(BaseModel):
    allow_entry: Optional[bool] = None
    allow_exit: Optional[bool] = None
    allow_trucks: Optional[bool] = None
    allow_buses: Optional[bool] = None
    allow_cars: Optional[bool] = None
    allow_two_wheelers: Optional[bool] = None
    maximum_vehicle_height: Optional[float] = Field(None, ge=0.0, le=20.0)
    maximum_vehicle_weight: Optional[float] = Field(None, ge=0.0, le=200.0)
    authorized_only: Optional[bool] = None
    working_hours_start: Optional[str] = Field(None, max_length=10)
    working_hours_end: Optional[str] = Field(None, max_length=10)
    remarks: Optional[str] = None
    is_active: Optional[bool] = None


class GateRuleInDBBase(GateRuleBase):
    id: UUID
    gate_id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class GateRuleResponse(GateRuleInDBBase):
    pass
