from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.transporter import TransporterResponse


class DriverBase(BaseModel):
    full_name: str = Field(..., max_length=150, description="Full Legal Name of Driver")
    license_number: str = Field(..., max_length=50, description="Driver License Number")
    phone_number: str = Field(..., max_length=20, description="Contact Phone Number")
    identity_card_no: Optional[str] = Field(None, max_length=50, description="Govt Issued ID / Aadhaar / SSN")
    transporter_id: Optional[UUID] = None
    is_active: bool = True


class DriverCreate(DriverBase):
    pass


class DriverUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=150)
    license_number: Optional[str] = Field(None, max_length=50)
    phone_number: Optional[str] = Field(None, max_length=20)
    identity_card_no: Optional[str] = Field(None, max_length=50)
    transporter_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class DriverInDBBase(DriverBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DriverResponse(DriverInDBBase):
    transporter: Optional[TransporterResponse] = None


class DriverPaginatedResponse(BaseModel):
    total: int
    items: List[DriverResponse]
