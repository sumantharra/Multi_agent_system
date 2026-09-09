from pathlib import Path

from app.core.config import Settings
from app.core.exceptions import ValidationAppError
from app.documents.storage.local import LocalUploadStorage
from app.documents.storage.protocol import StorageBackend


def get_storage(settings: Settings) -> StorageBackend:
    backend = settings.storage_backend.strip().lower()
    if backend == "local":
        return LocalUploadStorage(Path(settings.local_upload_dir))
    raise ValidationAppError(
        "Unsupported storage backend",
        details=[{"field": "storage_backend", "message": "only local is implemented"}],
    )
