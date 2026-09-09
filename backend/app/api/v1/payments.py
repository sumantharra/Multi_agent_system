from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, Header, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_database_session, require_dev_access
from app.schemas.hostel import PaginatedResponse
from app.schemas.payment import PaymentCreate, PaymentRead
from app.services.payment import PaymentService

router = APIRouter(
    prefix="/payments",
    tags=["payments"],
    dependencies=[Depends(require_dev_access)],
)


@router.post("", response_model=PaymentRead)
def create_payment(
    payload: PaymentCreate,
    response: Response,
    db: Session = Depends(get_database_session),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> PaymentRead:
    payment, created = PaymentService(db).create(payload, idempotency_key=idempotency_key)
    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return PaymentRead.model_validate(payment)


@router.get("", response_model=PaginatedResponse[PaymentRead])
def list_payments(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    hostel_id: UUID | None = Query(default=None),
    invoice_id: UUID | None = Query(default=None),
    date_from: date | None = Query(default=None, alias="from"),
    date_to: date | None = Query(default=None, alias="to"),
    db: Session = Depends(get_database_session),
) -> PaginatedResponse[PaymentRead]:
    result = PaymentService(db).list(
        page=page,
        page_size=page_size,
        hostel_id=hostel_id,
        invoice_id=invoice_id,
        date_from=date_from,
        date_to=date_to,
    )
    return PaginatedResponse[PaymentRead](
        items=[PaymentRead.model_validate(item) for item in result.items],
        page=result.page,
        page_size=result.page_size,
        total=result.total,
    )


@router.get("/{payment_id}", response_model=PaymentRead)
def get_payment(
    payment_id: UUID,
    db: Session = Depends(get_database_session),
) -> PaymentRead:
    payment = PaymentService(db).get(payment_id)
    return PaymentRead.model_validate(payment)
