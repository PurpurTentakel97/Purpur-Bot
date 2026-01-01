from typing import Optional

from attr import dataclass

from bot.chat.discord_client import DiscordClient
from bot.chat.twitch_client import TwitchClient
from bot.database.database import Database
from bot.helpers.config import ProgrammConfig


@dataclass
class ProgramParts:
    discord: Optional[DiscordClient] = None
    twitch: Optional[TwitchClient] = None
    _config: Optional[ProgrammConfig] = None
    _database: Optional[Database] = None

    @property
    def config(self) -> ProgrammConfig:
        if self._config is None:
            raise RuntimeError("ProgramParts.Config is None")
        return self._config

    @config.setter
    def config(self, config: ProgrammConfig) -> None:
        self._config = config

    def config_unwrapped(self) -> Optional[ProgrammConfig]:
        return self._config

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
