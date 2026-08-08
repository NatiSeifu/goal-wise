"""User-local date helpers."""

from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


def user_local_date(*, now: datetime, user_time_zone: str) -> date:
    return now.astimezone(ZoneInfo(user_time_zone)).date()


def local_week_start(*, now: datetime, user_time_zone: str) -> date:
    local_date = user_local_date(now=now, user_time_zone=user_time_zone)
    return local_date - timedelta(days=local_date.weekday())
