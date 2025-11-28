from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from core.database_core import get_db
from models.db_models.db_user_models import User
from models.api_models.api_user_models import UserCreate, UserRead, UserUpdate
from core.crud.crud_users import (
    create_user,
    get_user_by_email,
    list_users,
    get_user_by_id,
    update_user,
    delete_user,
)
from core.auth_core import hash_password, get_current_user

router = APIRouter(prefix="/users", tags=["User Operations"])


@router.post("", response_model=UserRead)
async def create_user_endpoint(
    data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    existing = await get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already in use")

    hashed = hash_password(data.password)
    user = await create_user(db, data, hashed)
    return user


@router.get("", response_model=list[UserRead])
async def list_users_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    return await list_users(db)


@router.get("/{user_id}", response_model=UserRead)
async def get_user_endpoint(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead)
async def update_user_endpoint(
    user_id: int,
    data: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.password is not None:
        data.password = hash_password(data.password)

    user = await update_user(db, user, data)
    return user


@router.delete("/{user_id}")
async def delete_user_endpoint(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await delete_user(db, user)
    return {"detail": f"User with id={id} deleted"}
