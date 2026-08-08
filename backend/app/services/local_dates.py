"""User-local date helpers."""

from datetime import date, datetime
from zoneinfo import ZoneInfo


def user_local_date(*, now: datetime, user_time_zone: str) -> date:
    return now.astimezone(ZoneInfo(user_time_zone)).date()
