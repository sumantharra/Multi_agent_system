import hashlib
import re
from uuid import UUID, uuid4

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.exceptions import NotFoundError, ValidationAppError
from app.documents.storage.factory import get_storage
from app.models.document import DOCUMENT_TYPES, PROCESSING_STATUSES, Document
from app.repositories.document import DocumentListResult, DocumentRepository
from app.repositories.hostel import HostelRepository

PDF_MIME = "application/pdf"
_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_file_name(name: str | None) -> str:
    raw = (name or "upload.pdf").strip() or "upload.pdf"
    cleaned = _SAFE_NAME.sub("_", raw.replace("\\", "/").split("/")[-1])
    if not cleaned.lower().endswith(".pdf"):
        cleaned = f"{cleaned}.pdf"
    return cleaned[:255]


def _validate_pdf(*, filename: str | None, content_type: str | None, data: bytes, max_bytes: int) -> None:
    if not data:
        raise ValidationAppError(
            "Empty file",
            details=[{"field": "file", "message": "file is empty"}],
        )
    if len(data) > max_bytes:
        raise ValidationAppError(
            "File too large",
            details=[{"field": "file", "message": f"max size is {max_bytes} bytes"}],
        )
    name = (filename or "").lower()
    mime = (content_type or "").split(";")[0].strip().lower()
    looks_pdf = name.endswith(".pdf") and data.startswith(b"%PDF")
    mime_ok = mime in ("", "application/pdf", "application/x-pdf")
    if not looks_pdf or not mime_ok:
        raise ValidationAppError(
            "Only PDF uploads are allowed",
            details=[{"field": "file", "message": "must be application/pdf"}],
        )


class DocumentService:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.settings = settings
        self.repo = DocumentRepository(db)
        self.hostels = HostelRepository(db)
        self.storage = get_storage(settings)

    def upload(
        self,
        *,
        hostel_id: UUID,
        data: bytes,
        filename: str | None,
        content_type: str | None,
        document_type: str,
        force: bool,
        uploaded_by: UUID | None = None,
    ) -> tuple[Document, bool]:
        hostel = self.hostels.get_by_id(hostel_id)
        if hostel is None:
            raise NotFoundError("Hostel not found")
        if document_type not in DOCUMENT_TYPES:
            raise ValidationAppError(
                "Invalid document type",
                details=[{"field": "document_type", "message": "unsupported value"}],
            )
        _validate_pdf(
            filename=filename,
            content_type=content_type,
            data=data,
            max_bytes=self.settings.max_upload_bytes,
        )
        content_hash = _sha256(data)
        existing = self.repo.get_by_hash_and_hostel(content_hash, hostel_id)
        if existing is not None and not force:
            return existing, False

        file_name = _safe_file_name(filename)
        if existing is not None and force:
            self.storage.put(existing.storage_key, data)
            existing.file_name = file_name
            existing.mime_type = PDF_MIME
            existing.document_type = document_type
            existing.processing_status = "queued"
            existing.extraction_status = "not_started"
            existing.extracted_payload = None
            existing.extraction_issues = None
            return self.repo.save(existing), False

        document_id = uuid4()
        storage_key = f"{hostel_id}/{document_id}.pdf"
        self.storage.put(storage_key, data)
        document = Document(
            id=document_id,
            hostel_id=hostel_id,
            file_name=file_name,
            storage_key=storage_key,
            mime_type=PDF_MIME,
            document_type=document_type,
            processing_status="queued",
            extraction_status="not_started",
            content_hash=content_hash,
            uploaded_by=uploaded_by,
        )
        return self.repo.add(document), True

    def get(self, document_id: UUID) -> Document:
        document = self.repo.get_by_id(document_id)
        if document is None:
            raise NotFoundError("Document not found")
        return document

    def list(
        self,
        *,
        page: int,
        page_size: int,
        hostel_id: UUID | None = None,
        processing_status: str | None = None,
    ) -> DocumentListResult:
        if processing_status is not None and processing_status not in PROCESSING_STATUSES:
            raise ValidationAppError(
                "Invalid processing status",
                details=[{"field": "processing_status", "message": "unsupported value"}],
            )
        return self.repo.list(
            page=page,
            page_size=page_size,
            hostel_id=hostel_id,
            processing_status=processing_status,
        )
