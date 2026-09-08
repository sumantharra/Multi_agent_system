from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_database_session, require_dev_access
from app.schemas.delivery import DeliveryCreate, DeliveryRead, DeliveryUpdate
from app.schemas.hostel import PaginatedResponse
from app.services.delivery import DeliveryService

router = APIRouter(
    prefix="/deliveries",
    tags=["deliveries"],
    dependencies=[Depends(require_dev_access)],
)


@router.post("", response_model=DeliveryRead, status_code=status.HTTP_201_CREATED)
def create_delivery(
    payload: DeliveryCreate,
    db: Session = Depends(get_database_session),
) -> DeliveryRead:
    delivery = DeliveryService(db).create(payload)
    return DeliveryRead.model_validate(delivery)


@router.get("", response_model=PaginatedResponse[DeliveryRead])
def list_deliveries(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    hostel_id: UUID | None = Query(default=None),
    date_from: date | None = Query(default=None, alias="from"),
    date_to: date | None = Query(default=None, alias="to"),
    db: Session = Depends(get_database_session),
) -> PaginatedResponse[DeliveryRead]:
    result = DeliveryService(db).list(
        page=page,
        page_size=page_size,
        hostel_id=hostel_id,
        date_from=date_from,
        date_to=date_to,
    )
    return PaginatedResponse[DeliveryRead](
        items=[DeliveryRead.model_validate(item) for item in result.items],
        page=result.page,
        page_size=result.page_size,
        total=result.total,
    )


@router.get("/{delivery_id}", response_model=DeliveryRead)
def get_delivery(
    delivery_id: UUID,
    db: Session = Depends(get_database_session),
) -> DeliveryRead:
    delivery = DeliveryService(db).get(delivery_id)
    return DeliveryRead.model_validate(delivery)


@router.put("/{delivery_id}", response_model=DeliveryRead)
def update_delivery(
    delivery_id: UUID,
    payload: DeliveryUpdate,
    db: Session = Depends(get_database_session),
) -> DeliveryRead:
    delivery = DeliveryService(db).update(delivery_id, payload)
    return DeliveryRead.model_validate(delivery)
