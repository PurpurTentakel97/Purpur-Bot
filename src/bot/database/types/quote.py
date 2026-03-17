from datetime import datetime

from pydantic import BaseModel


class Quote(BaseModel):
    id: int
    bot_id: int
    discord_id: int
    twitch_id: str
    timestamp: datetime
    quote: str
