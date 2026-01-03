from typing import final

from attr import dataclass


@final
@dataclass
class TwitchUserInfo:
    id_: str
    login: str
    display_name: str
