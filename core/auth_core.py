import os
from datetime import datetime, timedelta, timezone
from typing import Optional, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from core.database_core import get_db
from models.db_models.db_user_models import User
from core.crud.crud_users import (
    get_user_by_email,
    get_user_by_id
)
from core.crud.crud_tokens import get_token_session_by_jti


SECRET_KEY = os.getenv("SECRET_KEY", "rueckwand24ROCKS!")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
        data: dict,
        expires_delta: Optional[timedelta] = None
) -> tuple[str, datetime]:
    to_encode = data.copy()
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, expire


def decode_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


async def authenticate_user(
        db: AsyncSession,
        email: EmailStr,
        password: str
) -> Optional[User]:
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        jti: str = payload.get("jti")
        if user_id is None or jti is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    token_session = await get_token_session_by_jti(db, jti)
    if not token_session or token_session.is_revoked:
        raise credentials_exception

    user = await get_user_by_id(db, int(user_id))
    if user is None:
        raise credentials_exception
    return user
