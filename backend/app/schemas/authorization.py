from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class AuthorizationBase(BaseModel):
    vehicle_id: Optional[UUID] = None
    driver_id: Optional[UUID] = None
    plate_number: Optional[str] = Field(None, max_length=20)
    auth_type: str = Field("WHITELIST", max_length=30)
    purpose: Optional[str] = Field(None, max_length=200)
    destination: Optional[str] = Field(None, max_length=200)
    valid_from: datetime
    valid_to: Optional[datetime] = None
    max_stay_minutes: Optional[int] = None
    is_active: bool = True


class AuthorizationCreate(AuthorizationBase):
    pass


class AuthorizationUpdate(BaseModel):
    auth_type: Optional[str] = Field(None, max_length=30)
    purpose: Optional[str] = Field(None, max_length=200)
    destination: Optional[str] = Field(None, max_length=200)
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    max_stay_minutes: Optional[int] = None
    is_active: Optional[bool] = None


class AuthorizationInDBBase(AuthorizationBase):
    id: UUID
    created_by: Optional[UUID] = None
    approved_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AuthorizationResponse(AuthorizationInDBBase):
    vehicle_number: Optional[str] = None
    driver_name: Optional[str] = None


class AuthorizationPaginatedResponse(BaseModel):
    total: int
    items: List[AuthorizationResponse]
