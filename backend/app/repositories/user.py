from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, user_id: UUID) -> User | None:
        return self.db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(func.lower(User.email) == email.lower())
        return self.db.scalar(statement)

    def create(self, *, email: str, password_hash: str, role: str = "owner") -> User:
        user = User(email=email.lower(), password_hash=password_hash, role=role, active=True)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def count(self) -> int:
        return int(self.db.scalar(select(func.count()).select_from(User)) or 0)
