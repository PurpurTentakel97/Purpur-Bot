from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Quote(BaseModel):
    id: int
    bot_id: int
    discord_user_id: Optional[int]
    twitch_user_id: Optional[str]
    timestamp: datetime
    quote: str
