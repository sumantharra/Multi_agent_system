from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_database_session, require_dev_access
from app.core.config import Settings, get_settings
from app.schemas.dashboard import DashboardSummary
from app.services.dashboard import DashboardService

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"],
    dependencies=[Depends(require_dev_access)],
)


@router.get("", response_model=DashboardSummary)
def get_dashboard(
    db: Session = Depends(get_database_session),
    settings: Settings = Depends(get_settings),
) -> DashboardSummary:
    return DashboardService(db, settings).get_summary()
