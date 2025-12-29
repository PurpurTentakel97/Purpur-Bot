from typing import Optional

from attr import dataclass

from bot.discord_bot.discord_client import DiscordClient
from bot.twitch_bot.twitch_client import TwitchClient


@dataclass
class ProgramParts:
    discord: Optional[DiscordClient]
    twitch: Optional[TwitchClient]
