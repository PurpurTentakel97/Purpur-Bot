from datetime import UTC
from datetime import datetime
from datetime import timedelta

from bot.core.time import is_cooldown_passed_in_minutes


def test_is_cooldown_passed_in_minutes_not_passed() -> None:
    # Set last_timestamp to 5 minutes ago
    last_timestamp = datetime.now(UTC) - timedelta(minutes=5)
    # Cooldown is 10 minutes
    assert not is_cooldown_passed_in_minutes(last_timestamp, 10)


def test_is_cooldown_passed_in_minutes_passed() -> None:
    # Set last_timestamp to 15 minutes ago
    last_timestamp = datetime.now(UTC) - timedelta(minutes=15)
    # Cooldown is 10 minutes
    assert is_cooldown_passed_in_minutes(last_timestamp, 10)


def test_is_cooldown_passed_in_minutes_exactly() -> None:
    # Set last_timestamp to exactly 10 minutes ago
    last_timestamp = datetime.now(UTC) - timedelta(minutes=10)
    # Cooldown is 10 minutes
    assert is_cooldown_passed_in_minutes(last_timestamp, 10)
