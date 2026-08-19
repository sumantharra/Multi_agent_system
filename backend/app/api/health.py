from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_database_session
from app.core.config import Settings, get_settings
from app.core.exceptions import AppError
from app.schemas.health import HealthResponse, ReadyResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    settings: Settings = get_settings()
    return HealthResponse(
        service="multi-agent-api",
        environment=settings.app_env,
    )


@router.get("/health/ready", response_model=ReadyResponse)
def readiness_check(db: Session = Depends(get_database_session)) -> ReadyResponse:
    settings: Settings = get_settings()
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        raise AppError(
            code="DEPENDENCY_FAILED",
            message="Database is not ready",
            status_code=503,
            details=[{"field": "database", "message": str(exc)}],
        ) from exc

    return ReadyResponse(
        service="multi-agent-api",
        environment=settings.app_env,
        database="ok",
        request_id=str(uuid4()),
    )
