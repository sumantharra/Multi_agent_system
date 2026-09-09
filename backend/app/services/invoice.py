import calendar
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError, ValidationAppError
from app.models.invoice import Invoice, InvoiceItem
from app.repositories.delivery import DeliveryRepository
from app.repositories.hostel import HostelRepository
from app.repositories.invoice import InvoiceRepository
from app.schemas.invoice import InvoiceCreate

MONEY_QUANTUM = Decimal("0.01")


def _month_bounds(billing_month: str) -> tuple[date, date]:
    year, month = (int(part) for part in billing_month.split("-"))
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, 1), date(year, month, last_day)


def _as_money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)


@dataclass
class InvoiceListResult:
    items: list[Invoice]
    page: int
    page_size: int
    total: int


class InvoiceService:
    def __init__(self, db: Session) -> None:
        self.repo = InvoiceRepository(db)
        self.hostels = HostelRepository(db)
        self.deliveries = DeliveryRepository(db)

    def create(self, data: InvoiceCreate) -> Invoice:
        hostel = self.hostels.get_by_id(data.hostel_id)
        if hostel is None:
            raise NotFoundError("Hostel not found")

        existing = self.repo.get_by_hostel_and_month(data.hostel_id, data.billing_month)
        if existing is not None:
            raise ConflictError(
                "Invoice already exists for this hostel and billing month",
                details=[{"field": "billing_month", "message": "already exists"}],
            )

        period_start, period_end = _month_bounds(data.billing_month)
        deliveries = self.deliveries.list_for_hostel_period(
            data.hostel_id,
            period_start,
            period_end,
        )
        if not deliveries:
            raise ValidationAppError(
                "No deliveries found for this hostel and billing month",
                details=[{"field": "billing_month", "message": "no deliveries"}],
            )

        items: list[InvoiceItem] = []
        total_quantity = Decimal("0.000")
        subtotal = Decimal("0.00")
        for delivery in deliveries:
            amount = _as_money(delivery.total_quantity * delivery.rate_per_liter)
            total_quantity += delivery.total_quantity
            subtotal += amount
            items.append(
                InvoiceItem(
                    description=f"Delivery {delivery.delivery_date.isoformat()}",
                    quantity=delivery.total_quantity,
                    rate=delivery.rate_per_liter,
                    amount=amount,
                )
            )

        tax = _as_money(data.tax)
        adjustments = _as_money(data.adjustments)
        year_month = data.billing_month.replace("-", "")
        seq = self.repo.count_for_hostel(hostel.id) + 1
        invoice = Invoice(
            hostel_id=hostel.id,
            invoice_number=f"INV-{year_month}-{hostel.code}-{seq:03d}",
            billing_month=data.billing_month,
            period_start=period_start,
            period_end=period_end,
            total_quantity=total_quantity,
            subtotal=subtotal,
            tax=tax,
            adjustments=adjustments,
            total_amount=_as_money(subtotal + tax + adjustments),
            payment_status="unpaid",
            due_date=data.due_date or period_end,
            items=items,
        )
        try:
            created = self.repo.create(invoice)
        except IntegrityError as exc:
            raise ConflictError(
                "Invoice already exists for this hostel and billing month",
                details=[{"field": "billing_month", "message": "already exists"}],
            ) from exc
        if created is None:
            raise NotFoundError("Invoice not found")
        return created

    def get(self, invoice_id: UUID) -> Invoice:
        invoice = self.repo.get_by_id(invoice_id)
        if invoice is None:
            raise NotFoundError("Invoice not found")
        return invoice

    def list(
        self,
        *,
        page: int,
        page_size: int,
        hostel_id: UUID | None = None,
        billing_month: str | None = None,
        payment_status: str | None = None,
    ) -> InvoiceListResult:
        items, total = self.repo.list(
            page=page,
            page_size=page_size,
            hostel_id=hostel_id,
            billing_month=billing_month,
            payment_status=payment_status,
        )
        return InvoiceListResult(items=items, page=page, page_size=page_size, total=total)
