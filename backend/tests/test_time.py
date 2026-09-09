from datetime import UTC, date, datetime

from app.core.time import business_today


def test_ist_midnight_rolls_the_calendar_day_ahead_of_utc() -> None:
    before_ist_midnight = datetime(2026, 9, 9, 18, 29, tzinfo=UTC)
    after_ist_midnight = datetime(2026, 9, 9, 18, 31, tzinfo=UTC)

    assert business_today("Asia/Kolkata", now=before_ist_midnight) == date(2026, 9, 9)
    assert business_today("Asia/Kolkata", now=after_ist_midnight) == date(2026, 9, 10)
