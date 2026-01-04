from pydantic import BaseModel


class TwitchAuth(BaseModel):
    twitch_id: str
    access_token: str
    refresh_token: str
    expires_at: int


class Command(BaseModel):
    command: str
    message: str


class BotConfig(BaseModel):
    id: int
    twitch_user_id: str
    name: str


class TwitchChannel(BaseModel):
    id: int
    channel_name: str
