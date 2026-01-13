from typing import final

from pydantic import BaseModel


@final
class AliasDictEntry(BaseModel):
    id: int
    bot_id: int
    alias: str
    explanation: str
