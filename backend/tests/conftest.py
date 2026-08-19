from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker

import app.models  # noqa: F401
from app.api.deps import get_database_session
from app.core.config import Settings, get_settings
from app.database.base import Base
from app.main import app as fastapi_app


@pytest.fixture()
def settings() -> Settings:
    return Settings(
        app_env="development",
        allow_unauthenticated=True,
        database_url="sqlite:///:memory:",
        jwt_secret="test-secret-at-least-32-bytes-long",
        bootstrap_admin_password="test-admin-pass",
    )


@pytest.fixture()
def db_session(settings: Settings) -> Generator[Session]:
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(settings: Settings, db_session: Session) -> Generator[TestClient]:
    def override_settings() -> Settings:
        return settings

    def override_db() -> Generator[Session]:
        yield db_session

    fastapi_app.dependency_overrides[get_settings] = override_settings
    fastapi_app.dependency_overrides[get_database_session] = override_db
    with TestClient(fastapi_app) as test_client:
        yield test_client
    fastapi_app.dependency_overrides.clear()
