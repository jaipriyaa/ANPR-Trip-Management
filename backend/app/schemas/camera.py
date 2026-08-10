from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, field_validator
import re


class CameraBase(BaseModel):
    camera_name: str = Field(..., max_length=100)
    camera_position: str = Field("Entry Camera", max_length=50)  # Entry Camera, Exit Camera, Top View, Side View
    rtsp_url: str = Field(..., max_length=500)
    ip_address: Optional[str] = Field(None, max_length=50)
    camera_status: str = Field("Online", max_length=20)  # Online, Offline, Maintenance
    resolution: Optional[str] = Field("1080p", max_length=30)
    fps: Optional[int] = Field(30, ge=1, le=120)
    is_active: bool = True

    @field_validator("rtsp_url")
    @classmethod
    def validate_rtsp_url(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("RTSP URL cannot be empty.")
        v_clean = v.strip()
        # Accept rtsp://, http://, https://, or mock test streams
        if not (v_clean.startswith("rtsp://") or v_clean.startswith("http://") or v_clean.startswith("https://") or v_clean.startswith("mock://")):
            raise ValueError("RTSP URL must start with 'rtsp://', 'http://', or 'https://'.")
        return v_clean


class CameraCreate(CameraBase):
    gate_id: UUID


class CameraUpdate(BaseModel):
    camera_name: Optional[str] = Field(None, max_length=100)
    camera_position: Optional[str] = Field(None, max_length=50)
    rtsp_url: Optional[str] = Field(None, max_length=500)
    ip_address: Optional[str] = Field(None, max_length=50)
    camera_status: Optional[str] = Field(None, max_length=20)
    resolution: Optional[str] = Field(None, max_length=30)
    fps: Optional[int] = Field(None, ge=1, le=120)
    is_active: Optional[bool] = None

    @field_validator("rtsp_url")
    @classmethod
    def validate_rtsp_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v_clean = v.strip()
        if not (v_clean.startswith("rtsp://") or v_clean.startswith("http://") or v_clean.startswith("https://") or v_clean.startswith("mock://")):
            raise ValueError("RTSP URL must start with 'rtsp://', 'http://', or 'https://'.")
        return v_clean


class CameraInDBBase(CameraBase):
    id: UUID
    gate_id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class CameraResponse(CameraInDBBase):
    pass


class CameraPaginatedResponse(BaseModel):
    total: int
    items: List[CameraResponse]
