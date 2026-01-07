from typing import Any
from typing import Optional

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.database.types.counter import CounterDB

TABLE_NAME = "counter"
FIELD_NAME = "name"
FIELD_COUNTER = "count"


def select_counter(bot_id: int, name: str) -> Optional[CounterDB]:
    return PROGRAMM_PARTS.database.select_one(TABLE_NAME, where={"bot_id": bot_id, "name": name}, type_=CounterDB)


def select_counter_by_bot_id(bot_id: int) -> list[CounterDB]:
    return PROGRAMM_PARTS.database.select_all(TABLE_NAME, where={"bot_id": bot_id}, type_=CounterDB)


def insert_counter(bot_id: int, name: str) -> Optional[int]:
    return PROGRAMM_PARTS.database.insert(TABLE_NAME, {"bot_id": bot_id, "name": name})


def update_counter(bot_id: int, name: str, data: dict[str, Any]) -> bool:
    return PROGRAMM_PARTS.database.update(TABLE_NAME, where={"bot_id": bot_id, "name": name}, data=data)


def delete_counter(bot_id: int, name: str) -> bool:
    return PROGRAMM_PARTS.database.delete(TABLE_NAME, where={"bot_id": bot_id, "name": name})
