from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models.invoice import Invoice


class InvoiceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, invoice: Invoice) -> Invoice:
        self.db.add(invoice)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return self.get_by_id(invoice.id)

    def get_by_id(self, invoice_id: UUID) -> Invoice | None:
        statement = (
            select(Invoice)
            .options(selectinload(Invoice.items))
            .where(Invoice.id == invoice_id)
        )
        return self.db.scalar(statement)

    def get_by_hostel_and_month(self, hostel_id: UUID, billing_month: str) -> Invoice | None:
        statement = select(Invoice).where(
            Invoice.hostel_id == hostel_id,
            Invoice.billing_month == billing_month,
        )
        return self.db.scalar(statement)

    def count_for_hostel(self, hostel_id: UUID) -> int:
        statement = select(func.count()).select_from(Invoice).where(Invoice.hostel_id == hostel_id)
        return int(self.db.scalar(statement) or 0)

    def list(
        self,
        *,
        page: int,
        page_size: int,
        hostel_id: UUID | None = None,
        billing_month: str | None = None,
        payment_status: str | None = None,
    ) -> tuple[list[Invoice], int]:
        filters = []
        if hostel_id is not None:
            filters.append(Invoice.hostel_id == hostel_id)
        if billing_month is not None:
            filters.append(Invoice.billing_month == billing_month)
        if payment_status is not None:
            filters.append(Invoice.payment_status == payment_status)

        count_statement = select(func.count()).select_from(Invoice)
        list_statement = select(Invoice).order_by(
            Invoice.billing_month.desc(),
            Invoice.created_at.desc(),
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
