from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

import bcrypt
import jwt

from app.core.config import Settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(*, user_id: UUID, email: str, role: str, settings: Settings) -> str:
    expires = datetime.now(UTC) + timedelta(minutes=settings.jwt_access_ttl_minutes)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "type": "access",
        "exp": expires,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def create_refresh_token(*, user_id: UUID, settings: Settings) -> str:
    expires = datetime.now(UTC) + timedelta(days=settings.jwt_refresh_ttl_days)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expires,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str, settings: Settings) -> dict[str, Any]:
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
