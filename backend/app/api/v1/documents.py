from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_database_session, require_dev_access
from app.core.config import Settings, get_settings
from app.schemas.document import DocumentRead, PaginatedDocuments
from app.services.document import DocumentService

router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    dependencies=[Depends(require_dev_access)],
)


@router.post("/upload", response_model=DocumentRead)
async def upload_document(
    response: Response,
    hostel_id: UUID = Form(),
    document_type: str = Form(default="invoice"),
    force: bool = Form(default=False),
    file: UploadFile = File(),
    db: Session = Depends(get_database_session),
    settings: Settings = Depends(get_settings),
) -> DocumentRead:
    payload = await file.read()
    document, created = DocumentService(db, settings).upload(
        hostel_id=hostel_id,
        data=payload,
        filename=file.filename,
        content_type=file.content_type,
        document_type=document_type,
        force=force,
    )
    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return DocumentRead.model_validate(document)


@router.get("", response_model=PaginatedDocuments)
def list_documents(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    hostel_id: UUID | None = Query(default=None),
    processing_status: str | None = Query(default=None),
    db: Session = Depends(get_database_session),
    settings: Settings = Depends(get_settings),
) -> PaginatedDocuments:
    result = DocumentService(db, settings).list(
        page=page,
        page_size=page_size,
        hostel_id=hostel_id,
        processing_status=processing_status,
    )
    return PaginatedDocuments(
        items=[DocumentRead.model_validate(item) for item in result.items],
        page=result.page,
        page_size=result.page_size,
        total=result.total,
    )


@router.get("/{document_id}", response_model=DocumentRead)
def get_document(
    document_id: UUID,
    db: Session = Depends(get_database_session),
    settings: Settings = Depends(get_settings),
) -> DocumentRead:
    document = DocumentService(db, settings).get(document_id)
    return DocumentRead.model_validate(document)
