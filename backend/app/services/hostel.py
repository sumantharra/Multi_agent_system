from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.hostel import Hostel
from app.repositories.hostel import HostelRepository
from app.schemas.hostel import HostelCreate, HostelUpdate


@dataclass
class HostelListResult:
    items: list[Hostel]
    page: int
    page_size: int
    total: int


class HostelService:
    def __init__(self, db: Session) -> None:
        self.repo = HostelRepository(db)

    def create(self, data: HostelCreate) -> Hostel:
        existing = self.repo.get_by_code(data.code)
        if existing is not None:
            raise ConflictError(
                "Hostel code already exists",
                details=[{"field": "code", "message": "already exists"}],
            )
        try:
            return self.repo.create(data)
        except IntegrityError as exc:
            raise ConflictError(
                "Hostel code already exists",
                details=[{"field": "code", "message": "already exists"}],
            ) from exc

    def get(self, hostel_id: UUID) -> Hostel:
        hostel = self.repo.get_by_id(hostel_id)
        if hostel is None:
            raise NotFoundError("Hostel not found")
        return hostel

    def list(
        self,
        *,
        page: int,
        page_size: int,
        active: bool | None = None,
    ) -> HostelListResult:
        items, total = self.repo.list(page=page, page_size=page_size, active=active)
        return HostelListResult(items=items, page=page, page_size=page_size, total=total)

    def update(self, hostel_id: UUID, data: HostelUpdate) -> Hostel:
        hostel = self.get(hostel_id)
        if data.code is not None:
            existing = self.repo.get_by_code(data.code)
            if existing is not None and existing.id != hostel.id:
                raise ConflictError(
                    "Hostel code already exists",
                    details=[{"field": "code", "message": "already exists"}],
                )
        try:
            return self.repo.update(hostel, data)
        except IntegrityError as exc:
            raise ConflictError(
                "Hostel code already exists",
                details=[{"field": "code", "message": "already exists"}],
            ) from exc

    def deactivate(self, hostel_id: UUID) -> Hostel:
        hostel = self.get(hostel_id)
        if not hostel.active:
            return hostel
        return self.repo.soft_deactivate(hostel)
