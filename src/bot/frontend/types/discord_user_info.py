from pydantic import BaseModel


class DiscordUserInfo(BaseModel):
    id_: int
    username: str
    display_name: str
    avatar_url: str
