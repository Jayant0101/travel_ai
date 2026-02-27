from datetime import timedelta

import pytest
from fastapi import HTTPException

from auth import (
    create_access_token,
    decode_token,
    get_password_hash,
    verify_password,
)


def test_password_hash_and_verify_round_trip():
    password = "StrongPass123!"
    hashed = get_password_hash(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong-password", hashed) is False


def test_create_access_token_and_decode_round_trip():
    token = create_access_token(
        data={"sub": "user-123", "email": "user@example.com"},
        expires_delta=timedelta(minutes=10),
    )
    payload = decode_token(token)

    assert payload["sub"] == "user-123"
    assert payload["email"] == "user@example.com"
    assert "exp" in payload


def test_decode_token_invalid_raises_http_401():
    with pytest.raises(HTTPException) as exc:
        decode_token("not-a-valid-jwt")

    assert exc.value.status_code == 401
