from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

REVENUE_DEFINITION = (
    "Sum of invoice total_amount where payment_status is paid and billing_month "
    "equals the current month in BUSINESS_TIMEZONE."
)
PENDING_DEFINITION = (
    "Sum of remaining balances (total_amount minus recorded payments) for invoices "
    "with payment_status unpaid, partial, or overdue."
)


class DashboardSummary(BaseModel):
    as_of_date: date
    timezone: str
    currency_code: str
    active_hostel_count: int
    todays_supply: Decimal = Field(max_digits=12, decimal_places=3)
    revenue: Decimal = Field(max_digits=14, decimal_places=2)
    revenue_month: str
    revenue_definition: str
    pending_payments: Decimal = Field(max_digits=14, decimal_places=2)
    pending_definition: str
