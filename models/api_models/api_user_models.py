from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserRead(UserBase):
    id: int
    created_at: datetime

    # SQLAlchemy -> Pydantic
    model_config = ConfigDict(from_attributes=True)


class LoginData(BaseModel):
    email: EmailStr
    password: str
