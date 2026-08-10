from datetime import datetime
from typing import Optional, Any, Dict, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class AuditLogBase(BaseModel):
    user_id: Optional[UUID] = None
    action: str = Field(..., max_length=50)
    entity_type: str = Field(..., max_length=50)
    entity_id: Optional[str] = Field(None, max_length=50)
    details: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = Field(None, max_length=45)


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogInDBBase(AuditLogBase):
    id: UUID
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class AuditLogResponse(AuditLogInDBBase):
    username: Optional[str] = None


class AuditLogPaginatedResponse(BaseModel):
    total: int
    items: List[AuditLogResponse]
