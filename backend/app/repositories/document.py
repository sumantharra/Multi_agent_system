from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.document import Document


@dataclass
class DocumentListResult:
    items: list[Document]
    page: int
    page_size: int
    total: int


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, document_id: UUID) -> Document | None:
        return self.db.get(Document, document_id)

    def get_by_hash_and_hostel(self, content_hash: str, hostel_id: UUID) -> Document | None:
        statement = select(Document).where(
            Document.content_hash == content_hash,
            Document.hostel_id == hostel_id,
        )
        return self.db.scalar(statement)

    def add(self, document: Document) -> Document:
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def save(self, document: Document) -> Document:
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def list(
        self,
        *,
        page: int,
        page_size: int,
        hostel_id: UUID | None = None,
        processing_status: str | None = None,
    ) -> DocumentListResult:
        filters = []
        if hostel_id is not None:
            filters.append(Document.hostel_id == hostel_id)
        if processing_status is not None:
            filters.append(Document.processing_status == processing_status)

        count_statement = select(func.count()).select_from(Document)
        list_statement = select(Document).order_by(Document.created_at.desc())
        if filters:
            count_statement = count_statement.where(*filters)
            list_statement = list_statement.where(*filters)

        total = int(self.db.scalar(count_statement) or 0)
        items = list(
            self.db.scalars(
                list_statement.offset((page - 1) * page_size).limit(page_size)
            ).all()
        )
        return DocumentListResult(items=items, page=page, page_size=page_size, total=total)
