from datetime import timedelta

from core.auth_core import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
)


def test_hash_and_verify_password():
    password = "MyBigSecret123!"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)


def test_create_and_decode_token():
    data = {"sub": "123", "jti": "test_jti"}
    token, expires_at = create_access_token(data, expires_delta=timedelta(minutes=5))

    decoded = decode_token(token)
    assert decoded["sub"] == "123"
    assert decoded["jti"] == "test_jti"
    assert "exp" in decoded
