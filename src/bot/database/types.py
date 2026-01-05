from pydantic import BaseModel


class TwitchAuth(BaseModel):
    twitch_id: str
    access_token: str
    refresh_token: str
    expires_at: int


class DiscordAuth(BaseModel):
    discord_id: str
    access_token: str
    refresh_token: str
    expires_at: int


class BasicCommand(BaseModel):
    id: int
    bot_id: int
    command: str
    message: str


class BotConfig(BaseModel):
    id: int
    twitch_user_id: str
    name: str


class TwitchChannel(BaseModel):
    id: int
    bot_id: int
    channel_name: str


class DiscordServer(BaseModel):
    id: int
    bot_id: int
    server_id: str
    server_name: str
