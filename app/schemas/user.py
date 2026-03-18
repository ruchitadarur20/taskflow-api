from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role_id: int


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    is_active: bool
    role_id: int
    created_at: datetime

    class Config:
        from_attributes = True