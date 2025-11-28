from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.db_models.db_auth_models import TokenSession
from models.api_models.api_auth_models import TokenSessionCreate


async def create_token_session(
        db: AsyncSession,
        data: TokenSessionCreate
) -> TokenSession:
    session = TokenSession(
        user_id=data.user_id,
        jti=data.jti,
        expires_at=data.expires_at,
        is_revoked=data.is_revoked,
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_token_session_by_jti(
        db: AsyncSession,
        jti: str
) -> Optional[TokenSession]:
    result = await db.execute(select(TokenSession).where(TokenSession.jti == jti))
    return result.scalar_one_or_none()


async def revoke_token_session(
        db: AsyncSession,
        jti: str
) -> Optional[TokenSession]:
    session = await get_token_session_by_jti(db, jti)
    if not session:
        return None
    session.is_revoked = True
    await db.commit()
    await db.refresh(session)
    return session

async def get_token_session_by_id(
        db: AsyncSession,
        session_id: int
) -> Optional[TokenSession]:
    result = await db.execute(select(TokenSession).where(TokenSession.id == session_id))
    return result.scalar_one_or_none()


async def list_token_sessions(
        db: AsyncSession,
        user_id: Optional[int] = None
) -> Sequence[TokenSession]:
    stmt = select(TokenSession)
    if user_id is not None:
        stmt = stmt.where(TokenSession.user_id == user_id)
    result = await db.execute(stmt)
    return result.scalars().all()


async def delete_token_session(
        db: AsyncSession,
        session: TokenSession
) -> None:
    await db.delete(session)
    await db.commit()