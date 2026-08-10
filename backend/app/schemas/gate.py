from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator
import re

from app.schemas.camera import CameraResponse
from app.schemas.gate_rule import GateRuleResponse


class GateBase(BaseModel):
    gate_code: str = Field(..., max_length=50)
    gate_name: str = Field(..., max_length=100)
    gate_type: str = Field("Entry & Exit", max_length=30)  # Entry, Exit, Entry & Exit
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    status: str = Field("ACTIVE", max_length=20)
    is_active: bool = True

    @field_validator("gate_code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Gate code cannot be empty.")
        return v.strip().upper()


class GateCreate(GateBase):
    pass


class GateUpdate(BaseModel):
    gate_code: Optional[str] = Field(None, max_length=50)
    gate_name: Optional[str] = Field(None, max_length=100)
    gate_type: Optional[str] = Field(None, max_length=30)
    location: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    status: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None

    @field_validator("gate_code")
    @classmethod
    def validate_code(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Gate code cannot be empty.")
        return v.strip().upper()


class GateInDBBase(GateBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class GateResponse(GateInDBBase):
    camera_count: Optional[int] = 0
    cameras: Optional[List[CameraResponse]] = []
    rule: Optional[GateRuleResponse] = None


class GatePaginatedResponse(BaseModel):
    total: int
    items: List[GateResponse]
