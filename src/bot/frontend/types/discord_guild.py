from typing import Optional
from typing import TypedDict


class DiscordGuild(TypedDict):
    id: str
    name: str
    icon: Optional[str]
    owner: bool
    permissions: str
    features: list[str]
