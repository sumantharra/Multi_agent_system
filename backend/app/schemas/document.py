from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.schemas.hostel import PaginatedResponse

ProcessingStatus = Literal[
    "queued",
    "processing",
    "extracted",
    "pending_review",
    "confirmed",
    "rejected",
    "failed",
]
ExtractionStatus = Literal["not_started", "running", "succeeded", "failed", "skipped"]
DocumentType = Literal["invoice", "contract", "agreement", "statement", "other"]


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    hostel_id: UUID
    file_name: str
    storage_key: str
    mime_type: str
    document_type: str
    processing_status: str
    extraction_status: str
    extracted_payload: dict[str, Any] | None
    extraction_issues: list[dict[str, Any]] | None
    content_hash: str | None
    uploaded_by: UUID | None
    confirmed_at: datetime | None
    confirmed_by: UUID | None
    rejected_at: datetime | None
    rejected_by: UUID | None
    rejection_reason: str | None
    created_at: datetime


class PaginatedDocuments(PaginatedResponse[DocumentRead]):
    pass
