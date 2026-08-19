from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.exceptions import UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse


class AuthService:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.repo = UserRepository(db)
        self.settings = settings

    def ensure_bootstrap_admin(self) -> None:
        if self.repo.count() > 0:
            return
        self.repo.create(
            email=self.settings.bootstrap_admin_email,
            password_hash=hash_password(self.settings.bootstrap_admin_password),
            role="owner",
        )

    def login(self, payload: LoginRequest) -> tuple[TokenResponse, str]:
        user = self.repo.get_by_email(payload.email)
        if user is None or not user.active:
            raise UnauthorizedError("Invalid email or password")
        if not verify_password(payload.password, user.password_hash):
            raise UnauthorizedError("Invalid email or password")

        access = create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
            settings=self.settings,
        )
        refresh = create_refresh_token(user_id=user.id, settings=self.settings)
        token = TokenResponse(
            access_token=access,
            expires_in=self.settings.jwt_access_ttl_minutes * 60,
        )
        return token, refresh

    def get_user_from_access_token(self, token: str) -> User:
        try:
            payload = decode_token(token, self.settings)
        except Exception as exc:
            raise UnauthorizedError("Invalid or expired token") from exc
        if payload.get("type") != "access":
            raise UnauthorizedError("Invalid token type")
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedError("Invalid token subject")
        user = self.repo.get_by_id(UUID(user_id))
        if user is None or not user.active:
            raise UnauthorizedError("User not found or inactive")
        return user

    def refresh(self, refresh_token: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token, self.settings)
        except Exception as exc:
            raise UnauthorizedError("Invalid or expired refresh token") from exc
        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type")
        user = self.repo.get_by_id(UUID(payload["sub"]))
        if user is None or not user.active:
            raise UnauthorizedError("User not found or inactive")
        access = create_access_token(
            user_id=user.id,
            email=user.email,
            role=user.role,
            settings=self.settings,
        )
        return TokenResponse(
            access_token=access,
            expires_in=self.settings.jwt_access_ttl_minutes * 60,
        )
