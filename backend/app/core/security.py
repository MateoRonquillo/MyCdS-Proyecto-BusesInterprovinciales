import os
from datetime import datetime, timedelta, timezone

import jwt


def _get_secret_key() -> str:
    secret_key = os.getenv("JWT_SECRET_KEY")
    if not secret_key or len(secret_key) < 32:
        raise RuntimeError("JWT_SECRET_KEY must contain at least 32 characters")
    return secret_key


def create_access_token(subject: str) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
    return jwt.encode(
        {"sub": subject, "exp": expires_at},
        _get_secret_key(),
        algorithm="HS256",
    )


def decode_access_token(token: str) -> dict[str, object]:
    return jwt.decode(token, _get_secret_key(), algorithms=["HS256"])