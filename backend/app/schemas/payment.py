from datetime import date, datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

PaymentMethod = Literal["cash", "upi", "bank_transfer", "cheque", "other"]


class PaymentCreate(BaseModel):
    invoice_id: UUID
    amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    payment_date: date
    payment_method: PaymentMethod
    reference_number: str | None = Field(default=None, max_length=80)
    notes: str | None = None

    @field_validator("reference_number", "notes")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class PaymentUpdate(BaseModel):
    amount: Decimal | None = Field(default=None, gt=0, max_digits=14, decimal_places=2)
    payment_date: date | None = None
    payment_method: PaymentMethod | None = None
    reference_number: str | None = Field(default=None, max_length=80)
    notes: str | None = None

    @field_validator("reference_number", "notes")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    invoice_id: UUID
    hostel_id: UUID
    amount: Decimal
    payment_date: date
    payment_method: str
    reference_number: str | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
