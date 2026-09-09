from pathlib import Path


class LocalUploadStorage:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, key: str, data: bytes) -> None:
        path = self._safe_path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def exists(self, key: str) -> bool:
        return self._safe_path(key).is_file()

    def local_path(self, key: str) -> Path | None:
        path = self._safe_path(key)
        return path if path.is_file() else None

    def _safe_path(self, key: str) -> Path:
        relative = Path(key)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("storage key must be a relative path without ..")
        path = (self.root / relative).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError("storage key escaped upload directory")
        return path
