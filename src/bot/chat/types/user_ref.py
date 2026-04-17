from dataclasses import dataclass
from typing import Protocol
from typing import final


@final
class UserRef(Protocol):
    def render_mention(self) -> str: ...


@final
@dataclass(frozen=True)
class TwitchUserRef:
    name: str

    def render_mention(self) -> str:
        return f"@{self.name}"


@final
@dataclass(frozen=True)
class DiscordUserRef:
    discord_id: int

    def render_mention(self) -> str:
        return f"<@{self.discord_id}>"
