from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.hostel import Hostel
from app.schemas.hostel import HostelCreate, HostelUpdate


class HostelRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: HostelCreate) -> Hostel:
        hostel = Hostel(**data.model_dump())
        self.db.add(hostel)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        self.db.refresh(hostel)
        return hostel

    def get_by_id(self, hostel_id: UUID) -> Hostel | None:
        return self.db.get(Hostel, hostel_id)

    def get_by_code(self, code: str) -> Hostel | None:
        statement = select(Hostel).where(func.lower(Hostel.code) == code.lower())
        return self.db.scalar(statement)

    def list(
        self,
        *,
        page: int,
        page_size: int,
        active: bool | None = None,
    ) -> tuple[list[Hostel], int]:
        filters = []
        if active is not None:
            filters.append(Hostel.active.is_(active))

        count_statement = select(func.count()).select_from(Hostel)
        list_statement = select(Hostel).order_by(Hostel.name.asc())
        if filters:
            count_statement = count_statement.where(*filters)
            list_statement = list_statement.where(*filters)

        total = int(self.db.scalar(count_statement) or 0)
        items = list(
            self.db.scalars(
                list_statement.offset((page - 1) * page_size).limit(page_size)
            ).all()
        )
        return items, total

    def update(self, hostel: Hostel, data: HostelUpdate) -> Hostel:
        updates = data.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(hostel, field, value)
        self.db.add(hostel)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        self.db.refresh(hostel)
        return hostel

    def soft_deactivate(self, hostel: Hostel) -> Hostel:
        hostel.active = False
        self.db.add(hostel)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        self.db.refresh(hostel)
        return hostel
