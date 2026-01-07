from pydantic import BaseModel


class TwitchChannelDB(BaseModel):
    id: int
    bot_id: int
    channel_name: str
