from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_database_session
from app.core.config import Settings, get_settings
from app.core.exceptions import UnauthorizedError
from app.models.user import User
from app.schemas.auth import BrandResponse, LoginRequest, TokenResponse, UserRead
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE = "refresh_token"


@router.get("/brand", response_model=BrandResponse)
def get_brand(settings: Settings = Depends(get_settings)) -> BrandResponse:
    return BrandResponse(name=settings.app_name, domain=settings.brand_domain)


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    response: Response,
    db: Session = Depends(get_database_session),
    settings: Settings = Depends(get_settings),
) -> TokenResponse:
    token, refresh_token = AuthService(db, settings).login(payload)
    response.set_cookie(
        key=REFRESH_COOKIE,
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=not settings.is_development,
        max_age=settings.jwt_refresh_ttl_days * 24 * 60 * 60,
        path="/api/v1/auth",
    )
    return token


@router.post("/logout", status_code=204)
def logout(response: Response) -> None:
    response.delete_cookie(key=REFRESH_COOKIE, path="/api/v1/auth")


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(user)


@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(
    response: Response,
    db: Session = Depends(get_database_session),
    settings: Settings = Depends(get_settings),
    refresh_token: Annotated[str | None, Cookie(alias=REFRESH_COOKIE)] = None,
) -> TokenResponse:
    if not refresh_token:
        raise UnauthorizedError("Refresh token missing")
    return AuthService(db, settings).refresh(refresh_token)
