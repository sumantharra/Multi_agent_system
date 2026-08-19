from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.database.session import get_db
from app.models.user import User
from app.services.auth import AuthService

bearer_scheme = HTTPBearer(auto_error=False)


def get_database_session() -> Generator[Session]:
    yield from get_db()


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    db: Session = Depends(get_database_session),
    settings: Settings = Depends(get_settings),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Authentication required")
    return AuthService(db, settings).get_user_from_access_token(credentials.credentials)


def require_dev_access(
    settings: Settings = Depends(get_settings),
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)] = None,
    db: Session = Depends(get_database_session),
) -> None:
    """Allow JWT, or open access only when ALLOW_UNAUTHENTICATED=true in development."""
    if credentials is not None and credentials.scheme.lower() == "bearer":
        AuthService(db, settings).get_user_from_access_token(credentials.credentials)
        return
    if settings.allow_unauthenticated:
        if not settings.is_development:
            raise ForbiddenError(
                "ALLOW_UNAUTHENTICATED is only permitted when APP_ENV=development"
            )
        return
    raise UnauthorizedError("Authentication required")
