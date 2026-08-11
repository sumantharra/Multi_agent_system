from fastapi import APIRouter

from app.core.config import Settings, get_settings
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    settings: Settings = get_settings()
    return HealthResponse(
        service="multi-agent-api",
        environment=settings.app_env,
    )

