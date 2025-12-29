from typing import Optional

from attr import dataclass

from bot.discord_bot.discord_client import DiscordClient
from bot.helpers.config import ProgrammConfig
from bot.twitch_bot.twitch_client import TwitchClient


@dataclass
class ProgramParts:
    discord: Optional[DiscordClient]
    twitch: Optional[TwitchClient]
    config: Optional[ProgrammConfig]
