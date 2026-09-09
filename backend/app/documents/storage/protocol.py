from pathlib import Path
from typing import Protocol


class StorageBackend(Protocol):
    """Where original PDFs live. Local for V1; S3 can implement the same methods later."""

    def put(self, key: str, data: bytes) -> None:
        """Write bytes for key. Must not delete an existing object unless replacing the same key."""

    def exists(self, key: str) -> bool:
        """Return True if the original file is present."""

    def local_path(self, key: str) -> Path | None:
        """Filesystem path when the backend is local; None for remote backends."""
