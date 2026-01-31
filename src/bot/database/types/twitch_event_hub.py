from pydantic import BaseModel


class TwitchEventHubDB(BaseModel):
    id: int
    bot_id: int
    broadcaster_id: str
    message: str
    server_id: int
    channel_id: int
