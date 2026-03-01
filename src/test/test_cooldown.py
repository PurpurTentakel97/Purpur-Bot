from datetime import UTC
from datetime import datetime
from datetime import timedelta

import pytest

from bot.core.types.cooldown import Cooldown
from bot.core.types.cooldown import CooldownKey
from bot.core.types.cooldown import SubscriptionCooldownKey


@pytest.fixture
def cooldown() -> Cooldown[CooldownKey]:
    # Set a 2-second cooldown for testing
    return Cooldown[CooldownKey](2)


def test_cooldown_initial_state(cooldown: Cooldown[CooldownKey]) -> None:
    key = CooldownKey()
    assert not cooldown.contains(key)
    assert not cooldown.is_in_cooldown(key)


def test_cooldown_add_and_contains(cooldown: Cooldown[CooldownKey]) -> None:
    key = CooldownKey()
    cooldown.add(key)
    assert cooldown.contains(key)
    # If we just added it, it SHOULD be in cooldown.
    assert cooldown.is_in_cooldown(key)


def test_cooldown_expiration(cooldown: Cooldown[CooldownKey]) -> None:
    key = CooldownKey()
    cooldown.add(key)

    # Manually set the time back to simulate expiration
    cooldown.data[key] = datetime.now(UTC) - timedelta(seconds=3)

    # Offset (3s) < 2s is False.
    # So it returns False when it has expired.
    assert not cooldown.is_in_cooldown(key)
    # And it should have been removed.
    assert key not in cooldown.data


def test_shared_state_bug() -> None:
    c1 = Cooldown[CooldownKey](10)
    c2 = Cooldown[CooldownKey](20)
    key = CooldownKey()
    c1.add(key)
    # They should NOT share data.
    assert key not in c2.data


def test_subscription_cooldown_key() -> None:
    key1 = SubscriptionCooldownKey(bot_id=1, server_id=10, broadcast_id="abc")
    key2 = SubscriptionCooldownKey(bot_id=1, server_id=10, broadcast_id="abc")
    key3 = SubscriptionCooldownKey(bot_id=2, server_id=10, broadcast_id="abc")

    assert key1 == key2
    assert key1 != key3
    assert hash(key1) == hash(key2)
