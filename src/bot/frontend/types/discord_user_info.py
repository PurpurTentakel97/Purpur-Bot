from typing import final

from attr import dataclass


@final
@dataclass
class DiscordUserInfo:
    id_: int
    username: str
    display_name: str
    avatar_url: str
