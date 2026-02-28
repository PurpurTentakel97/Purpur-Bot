from datetime import UTC
from datetime import datetime
from datetime import timedelta

from attr import dataclass

from bot.core.app_context import APP_CONTEXT


@dataclass(frozen=True)
class CooldownKey:
    pass


@dataclass(frozen=True)
class SubscriptionCooldownKey(CooldownKey):
    bot_id: int
    server_id: int
    broadcast_id: str


@dataclass
class Cooldown[T: CooldownKey]:
    _cooldown_in_seconds: int
    _data: dict[T, datetime] = {}

    @property
    def data(self) -> dict[T, datetime]:
        return self._data

    @data.setter
    def data(self, data: dict[T, datetime]) -> None:
        self._data = data

    def contains(self, key: T) -> bool:
        return key in self._data

    def add(self, key: T) -> None:
        self._data[key] = datetime.now(UTC)

    def remove(self, key: T) -> None:
        del self._data[key]

    def is_in_cooldown(self, key: T) -> bool:
        if key not in self._data:
            return False

        offset = datetime.now(UTC) - self._data[key]
        is_in_cooldown = offset >= timedelta(seconds=self._cooldown_in_seconds)

        if not is_in_cooldown:
            self.remove(key)

        return is_in_cooldown


@dataclass
class CooldownsWrapper:
    twitch_live_subscription = Cooldown[SubscriptionCooldownKey](
        APP_CONTEXT.twitch_live_message_cooldown_in_seconds.value()
    )
