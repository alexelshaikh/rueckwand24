from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TokenSessionBase(BaseModel):
    jti: str
    expires_at: datetime
    is_revoked: bool = False


class TokenSessionCreate(TokenSessionBase):
    user_id: int


class TokenSessionRead(TokenSessionBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"