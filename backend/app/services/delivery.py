from dataclasses import dataclass
from datetime import date
from uuid import UUID

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.delivery import Delivery
from app.repositories.delivery import DeliveryRepository
from app.repositories.hostel import HostelRepository
from app.schemas.delivery import DeliveryCreate, DeliveryUpdate


@dataclass
class DeliveryListResult:
    items: list[Delivery]
    page: int
    page_size: int
    total: int


class DeliveryService:
    def __init__(self, db: Session) -> None:
        self.repo = DeliveryRepository(db)
        self.hostels = HostelRepository(db)

    def create(self, data: DeliveryCreate) -> Delivery:
        hostel = self.hostels.get_by_id(data.hostel_id)
        if hostel is None:
            raise NotFoundError("Hostel not found")
        if not hostel.active:
            raise NotFoundError("Hostel is not active")

        existing = self.repo.get_by_hostel_and_date(data.hostel_id, data.delivery_date)
        if existing is not None:
            raise ConflictError(
                "Delivery already exists for this hostel and date",
                details=[{"field": "delivery_date", "message": "already exists"}],
            )

        rate = data.rate_per_liter if data.rate_per_liter is not None else hostel.default_rate_per_liter
        delivery = Delivery(
            hostel_id=data.hostel_id,
            delivery_date=data.delivery_date,
            morning_quantity=data.morning_quantity,
            evening_quantity=data.evening_quantity,
            total_quantity=data.morning_quantity + data.evening_quantity,
            rate_per_liter=rate,
            notes=data.notes,
        )
        try:
            return self.repo.create(delivery)
        except IntegrityError as exc:
            raise ConflictError(
                "Delivery already exists for this hostel and date",
                details=[{"field": "delivery_date", "message": "already exists"}],
            ) from exc

    def get(self, delivery_id: UUID) -> Delivery:
        delivery = self.repo.get_by_id(delivery_id)
        if delivery is None:
            raise NotFoundError("Delivery not found")
        return delivery

    def list(
        self,
        *,
        page: int,
        page_size: int,
        hostel_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> DeliveryListResult:
        items, total = self.repo.list(
            page=page,
            page_size=page_size,
            hostel_id=hostel_id,
            date_from=date_from,
            date_to=date_to,
        )
        return DeliveryListResult(items=items, page=page, page_size=page_size, total=total)

    def update(self, delivery_id: UUID, data: DeliveryUpdate) -> Delivery:
        delivery = self.get(delivery_id)
        updates = data.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(delivery, field, value)
        delivery.total_quantity = delivery.morning_quantity + delivery.evening_quantity
        return self.repo.update(delivery)
