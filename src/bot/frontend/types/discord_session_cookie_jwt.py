from pydantic import BaseModel


class DiscordSessionCookie(BaseModel):
    user_id: int
    username: str
    display_name: str
    avatar_url: str
    exp: int
    iat: int
