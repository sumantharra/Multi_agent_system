from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_database_session, require_dev_access
from app.schemas.hostel import HostelCreate, HostelRead, HostelUpdate, PaginatedResponse
from app.services.hostel import HostelService

router = APIRouter(
    prefix="/hostels",
    tags=["hostels"],
    dependencies=[Depends(require_dev_access)],
)


@router.post("", response_model=HostelRead, status_code=status.HTTP_201_CREATED)
def create_hostel(
    payload: HostelCreate,
    db: Session = Depends(get_database_session),
) -> HostelRead:
    hostel = HostelService(db).create(payload)
    return HostelRead.model_validate(hostel)


@router.get("", response_model=PaginatedResponse[HostelRead])
def list_hostels(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    active: bool | None = Query(default=None),
    db: Session = Depends(get_database_session),
) -> PaginatedResponse[HostelRead]:
    result = HostelService(db).list(page=page, page_size=page_size, active=active)
    return PaginatedResponse[HostelRead](
        items=[HostelRead.model_validate(item) for item in result.items],
        page=result.page,
        page_size=result.page_size,
        total=result.total,
    )


@router.get("/{hostel_id}", response_model=HostelRead)
def get_hostel(
    hostel_id: UUID,
    db: Session = Depends(get_database_session),
) -> HostelRead:
    hostel = HostelService(db).get(hostel_id)
    return HostelRead.model_validate(hostel)


@router.put("/{hostel_id}", response_model=HostelRead)
def update_hostel(
    hostel_id: UUID,
    payload: HostelUpdate,
    db: Session = Depends(get_database_session),
) -> HostelRead:
    hostel = HostelService(db).update(hostel_id, payload)
    return HostelRead.model_validate(hostel)


@router.delete("/{hostel_id}", response_model=HostelRead)
def delete_hostel(
    hostel_id: UUID,
    db: Session = Depends(get_database_session),
) -> HostelRead:
    hostel = HostelService(db).deactivate(hostel_id)
    return HostelRead.model_validate(hostel)
