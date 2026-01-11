from pydantic import BaseModel


class BotConfigDB(BaseModel):
    id: int
    twitch_user_id: str
    name: str
