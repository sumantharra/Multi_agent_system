from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_database_session, require_dev_access
from app.schemas.hostel import PaginatedResponse
from app.schemas.invoice import InvoiceCreate, InvoiceRead, InvoiceSummary, PaymentStatus
from app.services.invoice import InvoiceService

router = APIRouter(
    prefix="/invoices",
    tags=["invoices"],
    dependencies=[Depends(require_dev_access)],
)


@router.post("", response_model=InvoiceRead, status_code=status.HTTP_201_CREATED)
def create_invoice(
    payload: InvoiceCreate,
    db: Session = Depends(get_database_session),
) -> InvoiceRead:
    invoice = InvoiceService(db).create(payload)
    return InvoiceRead.model_validate(invoice)


@router.get("", response_model=PaginatedResponse[InvoiceSummary])
def list_invoices(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    hostel_id: UUID | None = Query(default=None),
    billing_month: str | None = Query(default=None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$"),
    payment_status: PaymentStatus | None = Query(default=None),
    db: Session = Depends(get_database_session),
) -> PaginatedResponse[InvoiceSummary]:
    result = InvoiceService(db).list(
        page=page,
        page_size=page_size,
        hostel_id=hostel_id,
        billing_month=billing_month,
        payment_status=payment_status,
    )
    return PaginatedResponse[InvoiceSummary](
        items=[InvoiceSummary.model_validate(item) for item in result.items],
        page=result.page,
        page_size=result.page_size,
        total=result.total,
    )


@router.get("/{invoice_id}", response_model=InvoiceRead)
def get_invoice(
    invoice_id: UUID,
    db: Session = Depends(get_database_session),
) -> InvoiceRead:
    invoice = InvoiceService(db).get(invoice_id)
    return InvoiceRead.model_validate(invoice)
