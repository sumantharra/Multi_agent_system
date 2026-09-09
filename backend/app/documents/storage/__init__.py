from app.documents.storage.factory import get_storage
from app.documents.storage.local import LocalUploadStorage
from app.documents.storage.protocol import StorageBackend

__all__ = ["LocalUploadStorage", "StorageBackend", "get_storage"]
