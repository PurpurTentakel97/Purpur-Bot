from attr import dataclass


@dataclass
class TwitchOnlineMessageLight:
    broadcaster_id: str
    broadcaster_name: str
    channel_url: str
    stream_title: str
    category_name: str

    def advance(self, id_: int, discord_server_id: int, discord_channel_id: int, message: str) -> "TwitchOnlineMessage":
        return TwitchOnlineMessage(
            id=id_,
            discord_server_id=discord_server_id,
            discord_channel_id=discord_channel_id,
            broadcaster_id=self.broadcaster_id,
            message=message,
            broadcaster_name=self.broadcaster_name,
            channel_url=self.channel_url,
            stream_title=self.stream_title,
            category_name=self.category_name,
        )


@dataclass
class TwitchOnlineMessage(TwitchOnlineMessageLight):
    id: int
    discord_server_id: int
    discord_channel_id: int
    message: str
