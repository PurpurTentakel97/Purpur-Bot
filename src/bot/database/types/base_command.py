from pydantic import BaseModel


class BasicCommandDB(BaseModel):
    id: int
    bot_id: int
    command: str
    message: str
