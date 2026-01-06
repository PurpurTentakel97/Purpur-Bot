from typing import final

from attr import dataclass


@final
@dataclass
class DiscordUserInfo:
    id_: str
    username: str
    display_name: str
    avatar_url: str
