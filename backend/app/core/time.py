from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo

from app.core.config import get_settings


def business_today(timezone_name: str | None = None, *, now: datetime | None = None) -> date:
    """Calendar date in BUSINESS_TIMEZONE. Stored timestamps stay UTC."""
    name = timezone_name or get_settings().business_timezone
    tz = ZoneInfo(name)
    current = now if now is not None else datetime.now(tz)
    if current.tzinfo is None:
        current = current.replace(tzinfo=UTC)
    return current.astimezone(tz).date()
