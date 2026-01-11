from pydantic import BaseModel


class CounterDB(BaseModel):
    id: int
    bot_id: int
    name: str
    count: int
