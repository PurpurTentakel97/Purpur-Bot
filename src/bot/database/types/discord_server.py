from pydantic import BaseModel


class DiscordServerDB(BaseModel):
    id: int
    bot_id: int
    server_id: int
    server_name: str
    enabled: bool
