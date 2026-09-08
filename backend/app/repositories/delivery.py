from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.delivery import Delivery


class DeliveryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, delivery: Delivery) -> Delivery:
        self.db.add(delivery)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        self.db.refresh(delivery)
        return delivery

    def get_by_id(self, delivery_id: UUID) -> Delivery | None:
        return self.db.get(Delivery, delivery_id)

    def get_by_hostel_and_date(self, hostel_id: UUID, delivery_date: date) -> Delivery | None:
        statement = select(Delivery).where(
            Delivery.hostel_id == hostel_id,
            Delivery.delivery_date == delivery_date,
        )
        return self.db.scalar(statement)

    def list(
        self,
        *,
        page: int,
        page_size: int,
        hostel_id: UUID | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> tuple[list[Delivery], int]:
        filters = []
        if hostel_id is not None:
            filters.append(Delivery.hostel_id == hostel_id)
        if date_from is not None:
            filters.append(Delivery.delivery_date >= date_from)
        if date_to is not None:
            filters.append(Delivery.delivery_date <= date_to)

        count_statement = select(func.count()).select_from(Delivery)
        list_statement = select(Delivery).order_by(
            Delivery.delivery_date.desc(),
            Delivery.created_at.desc(),
        )
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

    def update(self, delivery: Delivery) -> Delivery:
        self.db.add(delivery)
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        self.db.refresh(delivery)
        return delivery
