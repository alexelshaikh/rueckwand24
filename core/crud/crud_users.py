from typing import Optional, Sequence
from pydantic import EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.db_models.db_user_models import User
from models.api_models.api_user_models import UserCreate, UserUpdate


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: EmailStr) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, data: UserCreate, hashed_password: str) -> User:
    user = User(email=data.email, hashed_password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def list_users(db: AsyncSession) -> Sequence[User]:
    result = await db.execute(select(User))
    return result.scalars().all()


async def update_user(db: AsyncSession, user: User, data: UserUpdate) -> User:
    if data.email is not None:
        user.email = data.email
    if data.password is not None:
        user.hashed_password = data.password  # assuming updated data contains the hashed password!
    if data.is_active is not None:
        user.is_active = data.is_active

    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user: User) -> None:
    await db.delete(user)
    await db.commit()