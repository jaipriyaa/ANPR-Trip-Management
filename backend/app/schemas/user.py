from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field, EmailStr


class UserBase(BaseModel):
    username: str = Field(..., max_length=50)
    email: EmailStr = Field(..., max_length=150)
    full_name: str = Field(..., max_length=150)
    role: str = Field("VIEWER", max_length=20)
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=150)
    email: Optional[EmailStr] = Field(None, max_length=150)
    role: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None


class UserInDBBase(UserBase):
    id: UUID
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class UserPaginatedResponse(BaseModel):
    total: int
    items: List[UserResponse]


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


class LoginRequest(BaseModel):
    username: str
    password: str
