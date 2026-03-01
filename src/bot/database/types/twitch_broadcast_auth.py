from pydantic import BaseModel


class TwitchBroadcastAuthDB(BaseModel):
    id: int
    bot_id: int
    channel_name: str
    twitch_user_id: str
    access_token: str
    refresh_token: str
    expires_at: int
