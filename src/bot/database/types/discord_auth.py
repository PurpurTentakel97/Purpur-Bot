from pydantic import BaseModel


class DiscordAuthDB(BaseModel):
    server_id: str
    access_token: str
    refresh_token: str
    expires_at: int
