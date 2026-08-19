from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PaginatedResponse[T](BaseModel):
    items: list[T]
    page: int
    page_size: int
    total: int


class HostelCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    code: str = Field(min_length=1, max_length=50)
    address: str | None = None
    contact_name: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=40)
    default_rate_per_liter: Decimal = Field(gt=0, max_digits=14, decimal_places=2)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("name is required")
        return stripped

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str) -> str:
        normalized = value.strip().upper()
        if not normalized:
            raise ValueError("code is required")
        return normalized

    @field_validator("address", "contact_name", "phone")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class HostelUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    code: str | None = Field(default=None, min_length=1, max_length=50)
    address: str | None = None
    contact_name: str | None = Field(default=None, max_length=120)
    phone: str | None = Field(default=None, max_length=40)
    default_rate_per_liter: Decimal | None = Field(
        default=None, gt=0, max_digits=14, decimal_places=2
    )
    active: bool | None = None

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            raise ValueError("name is required")
        return stripped

    @field_validator("code")
    @classmethod
    def normalize_code(cls, value: str | None) -> str | None:
        if value is None:
            return None
        normalized = value.strip().upper()
        if not normalized:
            raise ValueError("code is required")
        return normalized

    @field_validator("address", "contact_name", "phone")
    @classmethod
    def empty_to_none(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        return stripped or None


class HostelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    code: str
    address: str | None
    contact_name: str | None
    phone: str | None
    default_rate_per_liter: Decimal
    active: bool
    created_at: datetime
    updated_at: datetime
