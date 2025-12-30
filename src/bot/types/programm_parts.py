from typing import Optional

from attr import dataclass

from bot.chat.discord_client import DiscordClient
from bot.chat.twitch_client import TwitchClient
from bot.helpers.config import ProgrammConfig


@dataclass
class ProgramParts:
    discord: Optional[DiscordClient]
    twitch: Optional[TwitchClient]
    config: Optional[ProgrammConfig]
