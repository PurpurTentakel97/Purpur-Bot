from pydantic import BaseModel


class TwitchAuthDB(BaseModel):
    twitch_id: str
    access_token: str
    refresh_token: str
    expires_at: int
