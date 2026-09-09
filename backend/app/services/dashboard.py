from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.time import business_today
from app.repositories.dashboard import DashboardRepository
from app.schemas.dashboard import (
    PENDING_DEFINITION,
    REVENUE_DEFINITION,
    DashboardSummary,
)

QTY_QUANTUM = Decimal("0.001")
MONEY_QUANTUM = Decimal("0.01")


def _qty(value: Decimal) -> Decimal:
    return value.quantize(QTY_QUANTUM, rounding=ROUND_HALF_UP)


def _money(value: Decimal) -> Decimal:
    return value.quantize(MONEY_QUANTUM, rounding=ROUND_HALF_UP)


class DashboardService:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.settings = settings
        self.repo = DashboardRepository(db)

    def get_summary(self) -> DashboardSummary:
        today = business_today(self.settings.business_timezone)
        revenue_month = f"{today.year:04d}-{today.month:02d}"
        return DashboardSummary(
            as_of_date=today,
            timezone=self.settings.business_timezone,
            currency_code=self.settings.currency_code,
            active_hostel_count=self.repo.count_active_hostels(),
            todays_supply=_qty(self.repo.sum_supply_on(today)),
            revenue=_money(self.repo.sum_paid_invoice_totals(revenue_month)),
            revenue_month=revenue_month,
            revenue_definition=REVENUE_DEFINITION,
            pending_payments=_money(self.repo.sum_pending_balances()),
            pending_definition=PENDING_DEFINITION,
        )
