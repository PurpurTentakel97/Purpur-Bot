from attr import dataclass


@dataclass
class TwitchOnlineMessage:
    id: int
    discord_server_id: int
    discord_channel_id: int
    message: str
