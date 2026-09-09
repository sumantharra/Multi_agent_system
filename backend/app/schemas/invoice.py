import re
from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

BILLING_MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
PaymentStatus = Literal["unpaid", "partial", "paid", "overdue"]


class InvoiceCreate(BaseModel):
    hostel_id: UUID
    billing_month: str
    tax: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=14, decimal_places=2)
    adjustments: Decimal = Field(default=Decimal("0.00"), max_digits=14, decimal_places=2)
    due_date: date | None = None

    @field_validator("billing_month")
    @classmethod
    def validate_billing_month(cls, value: str) -> str:
        normalized = value.strip()
        if not BILLING_MONTH_PATTERN.fullmatch(normalized):
            raise ValueError("billing_month must be YYYY-MM")
        return normalized


class InvoiceItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    description: str
    quantity: Decimal
    rate: Decimal
    amount: Decimal


class InvoiceSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    hostel_id: UUID
    invoice_number: str
    billing_month: str
    period_start: date
    period_end: date
    total_quantity: Decimal
    subtotal: Decimal
    tax: Decimal
    adjustments: Decimal
    total_amount: Decimal
    payment_status: str
    due_date: date
    source_document_id: UUID | None
    created_at: datetime
    updated_at: datetime


class InvoiceRead(InvoiceSummary):
    items: list[InvoiceItemRead]
