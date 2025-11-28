from typing import Annotated
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr, TypeAdapter, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from core.database_core import get_db
from models.db_models.db_user_models import User
from models.api_models.api_auth_models import (
    Token,
    TokenSessionCreate,
    TokenSessionRead
)
from core.crud.crud_tokens import (
    create_token_session,
    get_token_session_by_jti,
    list_token_sessions,
    get_token_session_by_id,
    delete_token_session,
)
from core.auth_core import (
    oauth2_scheme,
    authenticate_user,
    create_access_token,
    decode_token,
    get_current_user,
)

EMAIL_ADAPTER = TypeAdapter(EmailStr)
router = APIRouter(tags=["Authentication Operations"])


@router.post("/login", response_model=Token)
async def login(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Annotated[AsyncSession, Depends(get_db)]
):
    try:
        email = EMAIL_ADAPTER.validate_python(form_data.username)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your entered username is not a valid email",
        )

    user = await authenticate_user(db, email, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    jti = str(uuid4())
    access_token, expires_at = create_access_token(
        data={"sub": str(user.id), "jti": jti}
    )

    session_data = TokenSessionCreate(
        user_id=user.id,
        jti=jti,
        expires_at=expires_at,
        is_revoked=False,
    )
    await create_token_session(db, session_data)

    return Token(access_token=access_token)


@router.post("/logout")
async def logout(
    current_user: Annotated[User, Depends(get_current_user)],
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)]
):
    payload = decode_token(token)
    jti = payload.get("jti")
    if not jti:
        raise HTTPException(status_code=400, detail="Invalid token")

    session = await get_token_session_by_jti(db, jti)
    if not session:
        raise HTTPException(status_code=400, detail="Session not found - you are already logged out, buddy!")

    session.is_revoked = True
    await db.commit()
    return {"detail": "Logged out successfully"}


#########################################################################
########################## Token Session Endpoints ######################
#########################################################################

@router.get("/token-sessions", response_model=list[TokenSessionRead])
async def list_token_sessions_endpoint(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    sessions = await list_token_sessions(db, user_id=current_user.id)
    return sessions


@router.get("/token-sessions/{session_id}", response_model=TokenSessionRead)
async def get_token_session_endpoint(
    session_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    session = await get_token_session_by_id(db, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.delete("/token-sessions/{session_id}")
async def delete_token_session_endpoint(
    session_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    session = await get_token_session_by_id(db, session_id)
    if not session or session.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Session not found")

    await delete_token_session(db, session)
    return {"detail": f"Requested session with id={session_id} was deleted successfully"}
