from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

# Repo root .env (../.env when running from backend/)
_ROOT_ENV = Path(__file__).resolve().parents[3] / ".env"
_LOCAL_ENV = Path(".env")


class Settings(BaseSettings):
    app_name: str = "RR Vijaya Milk Agencies"
    app_env: str = "development"
    log_level: str = "INFO"
    cors_origins: Annotated[list[str], NoDecode] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/multi_agent"
    allow_unauthenticated: bool = False
    business_timezone: str = "Asia/Kolkata"
    currency_code: str = "INR"
    brand_domain: str = "rrvijayamilkagencies.com"
    jwt_secret: str = "change-me-dev-only"
    jwt_access_ttl_minutes: int = 15
    jwt_refresh_ttl_days: int = 7
    bootstrap_admin_email: str = "admin@local.test"
    bootstrap_admin_password: str = "change-me"

    model_config = SettingsConfigDict(
        env_file=(_ROOT_ENV if _ROOT_ENV.exists() else _LOCAL_ENV),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def is_development(self) -> bool:
        return self.app_env.lower() == "development"


@lru_cache
def get_settings() -> Settings:
    return Settings()
