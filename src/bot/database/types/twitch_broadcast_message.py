from pydantic import BaseModel


class TwitchBroadcastMessageDB(BaseModel):
    id: int
    bot_id: int
    channel_name: str
    message: str
    interval_in_minutes: int
    enabled: bool
