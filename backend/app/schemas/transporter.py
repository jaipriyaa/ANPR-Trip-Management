from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class TransporterBase(BaseModel):
    code: str = Field(..., max_length=50, description="Unique identifier code for the transporter company")
    company_name: str = Field(..., max_length=150, description="Full legal name of the transporter company")
    contact_person: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = Field(None, max_length=150)
    is_active: bool = True

    @field_validator("email", "contact_person", "phone", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v


class TransporterCreate(TransporterBase):
    pass


class TransporterUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=50)
    company_name: Optional[str] = Field(None, max_length=150)
    contact_person: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = Field(None, max_length=150)
    is_active: Optional[bool] = None

    @field_validator("email", "contact_person", "phone", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        if v == "" or v is None:
            return None
        return v


class TransporterInDBBase(TransporterBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TransporterResponse(TransporterInDBBase):
    pass


class TransporterPaginatedResponse(BaseModel):
    total: int
    items: List[TransporterResponse]