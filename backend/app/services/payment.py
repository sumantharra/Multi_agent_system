from dataclasses import dataclass
from datetime import date, datetime
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID
from zoneinfo import ZoneInfo

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import NotFoundError
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.repositories.invoice import InvoiceRepository
from app.repositories.payment import PaymentRepository
from app.schemas.payment import PaymentCreate

MONEY_QUANTUM = Decimal("0.01")


def _as_money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)


def business_today() -> date:
    timezone = ZoneInfo(get_settings().business_timezone)
    return datetime.now(timezone).date()


def compute_payment_status(
    *,
    total_amount: Decimal,
    paid_amount: Decimal,
    due_date: date,
    today: date,
) -> str:
    total = _as_money(total_amount)
    paid = _as_money(paid_amount)
    if paid >= total:
        return "paid"
    if due_date < today:
        return "overdue"
    if paid > Decimal("0.00"):
        return "partial"
    return "unpaid"


@dataclass
class PaymentListResult:
    items: list[Payment]
    page: int
    page_size: int
    total: int


class PaymentService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = PaymentRepository(db)
        self.invoices = InvoiceRepository(db)

    def _refresh_invoice_status(self, invoice: Invoice) -> None:
        paid = self.repo.sum_for_invoice(invoice.id)
        invoice.payment_status = compute_payment_status(
            total_amount=invoice.total_amount,
            paid_amount=paid,
            due_date=invoice.due_date,
            today=business_today(),
        )

    def create(
        self,
        data: PaymentCreate,
        *,
        idempotency_key: str | None = None,
    ) -> tuple[Payment, bool]:
        key = idempotency_key.strip() if idempotency_key else None
        if key:
            existing = self.repo.get_by_idempotency_key(key)
            if existing is not None:
                return existing, False

        invoice = self.invoices.get_by_id(data.invoice_id)
        if invoice is None:
            raise NotFoundError("Invoice not found")

        payment = Payment(
            invoice_id=invoice.id,
            hostel_id=invoice.hostel_id,
            amount=_as_money(data.amount),
            payment_date=data.payment_date,
            payment_method=data.payment_method,
            reference_number=data.reference_number,
            notes=data.notes,
            idempotency_key=key,
        )
        self.db.add(payment)
        self.db.flush()
        self._refresh_invoice_status(invoice)
        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            if key:
                replay = self.repo.get_by_idempotency_key(key)
                if replay is not None:
                    return replay, False
            raise
        self.db.refresh(payment)
        return payment, True

    def get(self, payment_id: UUID) -> Payment:
        payment = self.repo.get_by_id(payment_id)
        if payment is None:
            raise NotFoundError("Payment not found")
        return payment

    def list(
        self,
        *,
        page: int,
        page_size: int,
        hostel_id: UUID | None = None,
        invoice_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> PaymentListResult:
        items, total = self.repo.list(
            page=page,
            page_size=page_size,
            hostel_id=hostel_id,
            invoice_id=invoice_id,
            date_from=date_from,
            date_to=date_to,
        )
        return PaymentListResult(items=items, page=page, page_size=page_size, total=total)
