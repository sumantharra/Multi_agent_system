from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DeliveryCreate(BaseModel):
    hostel_id: UUID
    delivery_date: date
    morning_quantity: Decimal = Field(ge=0, max_digits=12, decimal_places=3)
    evening_quantity: Decimal = Field(ge=0, max_digits=12, decimal_places=3)
    rate_per_liter: Decimal | None = Field(default=None, gt=0, max_digits=14, decimal_places=2)
    notes: str | None = None

    @field_validator("notes")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class DeliveryUpdate(BaseModel):
    morning_quantity: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=3)
    evening_quantity: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=3)
    rate_per_liter: Decimal | None = Field(default=None, gt=0, max_digits=14, decimal_places=2)
    notes: str | None = None

    @field_validator("notes")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class DeliveryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    hostel_id: UUID
    delivery_date: date
    morning_quantity: Decimal
    evening_quantity: Decimal
    total_quantity: Decimal
    rate_per_liter: Decimal
    notes: str | None
    created_by: UUID | None
    created_at: datetime
    updated_at: datetime
