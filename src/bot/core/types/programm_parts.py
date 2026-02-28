from typing import TYPE_CHECKING
from typing import Optional

from attr import dataclass

from bot.chat.discord_client import DiscordClient
from bot.chat.twitch_client import TwitchClient
from bot.core.types.broadcast_message_storrage import BroadcastMessageStorage
from bot.core.types.cooldown import CooldownsWrapper
from bot.database.database import Database

if TYPE_CHECKING:
    from bot.core.twitch_event_hub import TwitchEventHub


@dataclass
class ProgramParts:
    discord: Optional[DiscordClient] = None
    twitch: Optional[TwitchClient] = None
    event_hub: Optional["TwitchEventHub"] = None
    _database: Optional[Database] = None
    broadcast: Optional[BroadcastMessageStorage] = None
    _cooldowns: Optional[CooldownsWrapper] = None

    @property
    def database(self) -> Database:
        if self._database is None:
            raise RuntimeError("ProgramParts.Database is None")
        return self._database

    @database.setter
    def database(self, database: Database) -> None:
        self._database = database

    def database_unwrapped(self) -> Optional[Database]:
        return self._database

    @property
    def cooldowns(self) -> CooldownsWrapper:
        if self._cooldowns is None:
            raise RuntimeError("ProgramParts.Cooldowns is None")
        return self._cooldowns

    @cooldowns.setter
    def cooldowns(self, cooldowns: CooldownsWrapper) -> None:
        self._cooldowns = cooldowns

    def cooldowns_unwrapped(self) -> Optional[CooldownsWrapper]:
        return self._cooldowns


PROGRAMM_PARTS = ProgramParts()
