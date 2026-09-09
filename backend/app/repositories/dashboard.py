from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.delivery import Delivery
from app.models.hostel import Hostel
from app.models.invoice import Invoice
from app.models.payment import Payment

PENDING_STATUSES = ("unpaid", "partial", "overdue")


class DashboardRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def count_active_hostels(self) -> int:
        value = self.db.scalar(
            select(func.count()).select_from(Hostel).where(Hostel.active.is_(True))
        )
        return int(value or 0)

    def sum_supply_on(self, delivery_date: date) -> Decimal:
        value = self.db.scalar(
            select(func.coalesce(func.sum(Delivery.total_quantity), 0)).where(
                Delivery.delivery_date == delivery_date
            )
        )
        return Decimal(str(value or 0))

    def sum_paid_invoice_totals(self, billing_month: str) -> Decimal:
        value = self.db.scalar(
            select(func.coalesce(func.sum(Invoice.total_amount), 0)).where(
                Invoice.payment_status == "paid",
                Invoice.billing_month == billing_month,
            )
        )
        return Decimal(str(value or 0))

    def sum_pending_balances(self) -> Decimal:
        paid_subq = (
            select(
                Payment.invoice_id.label("invoice_id"),
                func.coalesce(func.sum(Payment.amount), 0).label("paid_amount"),
            )
            .group_by(Payment.invoice_id)
            .subquery()
        )
        remaining = Invoice.total_amount - func.coalesce(paid_subq.c.paid_amount, 0)
        value = self.db.scalar(
            select(func.coalesce(func.sum(remaining), 0))
            .select_from(Invoice)
            .outerjoin(paid_subq, paid_subq.c.invoice_id == Invoice.id)
            .where(Invoice.payment_status.in_(PENDING_STATUSES))
        )
        return Decimal(str(value or 0))
