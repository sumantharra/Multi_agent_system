from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.payment import Payment


class PaymentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, payment: Payment) -> Payment:
        self.db.add(payment)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        self.db.refresh(payment)
        return payment

    def get_by_id(self, payment_id: UUID) -> Payment | None:
        return self.db.get(Payment, payment_id)

    def get_by_idempotency_key(self, key: str) -> Payment | None:
        statement = select(Payment).where(Payment.idempotency_key == key)
        return self.db.scalar(statement)

    def sum_for_invoice(self, invoice_id: UUID, *, exclude_id: UUID | None = None) -> Decimal:
        statement = select(func.coalesce(func.sum(Payment.amount), 0)).where(
            Payment.invoice_id == invoice_id
        )
        if exclude_id is not None:
            statement = statement.where(Payment.id != exclude_id)
        return Decimal(str(self.db.scalar(statement) or 0))

    def list(
        self,
        *,
        page: int,
        page_size: int,
        hostel_id: UUID | None = None,
        invoice_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> tuple[list[Payment], int]:
        filters = []
        if hostel_id is not None:
            filters.append(Payment.hostel_id == hostel_id)
        if invoice_id is not None:
            filters.append(Payment.invoice_id == invoice_id)
        if date_from is not None:
            filters.append(Payment.payment_date >= date_from)
        if date_to is not None:
            filters.append(Payment.payment_date <= date_to)

        count_statement = select(func.count()).select_from(Payment)
        list_statement = select(Payment).order_by(
            Payment.payment_date.desc(),
            Payment.created_at.desc(),
        )
        if filters:
            count_statement = count_statement.where(*filters)
            list_statement = list_statement.where(*filters)

        total = int(self.db.scalar(count_statement) or 0)
        items = list(
            self.db.scalars(
                list_statement.offset((page - 1) * page_size).limit(page_size)
            ).all()
        )
        return items, total
