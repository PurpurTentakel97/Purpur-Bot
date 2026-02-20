from datetime import UTC
from datetime import datetime
from datetime import timedelta


def is_cooldown_passed_in_minutes(last_timestamp: datetime, cooldown_minutes: int) -> bool:
    now = datetime.now(UTC)
    offset = now - last_timestamp
    return offset >= timedelta(minutes=cooldown_minutes)
