from datetime import datetime
from typing import Optional, Any, Dict, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class TripEventBase(BaseModel):
    trip_id: UUID
    event_type: str = Field(..., max_length=30)
    description: Optional[str] = None
    event_metadata: Optional[Dict[str, Any]] = Field(None, alias="metadata")


class TripEventCreate(TripEventBase):
    pass


class TripEventInDBBase(TripEventBase):
    id: UUID
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class TripEventResponse(TripEventInDBBase):
    pass


class TripEventPaginatedResponse(BaseModel):
    total: int
    items: List[TripEventResponse]
