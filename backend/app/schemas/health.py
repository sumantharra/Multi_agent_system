from typing import Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str
    environment: str


class ReadyResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str
    environment: str
    database: Literal["ok"]
    request_id: str = Field(description="Correlation id for this readiness probe")


class ErrorDetail(BaseModel):
    field: str | None = None
    message: str


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)
    request_id: str


class ErrorResponse(BaseModel):
    error: ErrorBody
