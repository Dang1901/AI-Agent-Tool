from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime

class UserResponse(BaseModel):
    id: int
    email: str
    name: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    is_verified: bool = False
    is_active: bool = True
    department: Optional[str] = None
    position: Optional[str] = None
    location: Optional[str] = None
    clearance_level: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    dob: Optional[date] = None
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    location: Optional[str] = None
    clearance_level: Optional[str] = None

class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    is_verified: Optional[bool] = None
    is_active: Optional[bool] = None
    department: Optional[str] = None
    position: Optional[str] = None
    location: Optional[str] = None
    clearance_level: Optional[str] = None
    
class UserLogin(BaseModel):
    email: EmailStr
    password: str
