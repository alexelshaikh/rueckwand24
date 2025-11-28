from datetime import datetime
from typing import List
from pydantic import EmailStr
from sqlalchemy import String, Integer, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.db_models.db_base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[EmailStr] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    sessions: Mapped[List["TokenSession"]] = relationship(back_populates="user", cascade="all, delete-orphan")

