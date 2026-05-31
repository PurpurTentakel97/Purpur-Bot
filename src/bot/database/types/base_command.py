from pydantic import BaseModel

from bot.core.types.permission_level import PermissionLevel


class BasicCommandDB(BaseModel):
    id: int
    bot_id: int
    command: str
    message: str
    enabled: bool
    permission_level: PermissionLevel
