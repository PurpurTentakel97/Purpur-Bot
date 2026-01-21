from typing import Optional

from attr import dataclass

from bot.chat.discord_client import DiscordClient
from bot.chat.twitch_client import TwitchClient
from bot.core.types.broadcast_message_storrage import BroadcastMessageStorage
from bot.database.database import Database


@dataclass
class ProgramParts:
    discord: Optional[DiscordClient] = None
    twitch: Optional[TwitchClient] = None
    _database: Optional[Database] = None
    broadcast: Optional[BroadcastMessageStorage] = None

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


PROGRAMM_PARTS = ProgramParts()
