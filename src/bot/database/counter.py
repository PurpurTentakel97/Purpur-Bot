from typing import Any

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.database.types.counter import CounterDB

TABLE_NAME = "counter"
FIELD_NAME = "name"
FIELD_COUNTER = "count"


def select_counter(bot_id: int, name: str) -> Result[CounterDB]:
    return PROGRAMM_PARTS.database.select_one(TABLE_NAME, where={"bot_id": bot_id, "name": name}, type_=CounterDB)


def select_counter_by_bot_id(bot_id: int) -> Result[list[CounterDB]]:
    return PROGRAMM_PARTS.database.select_all(TABLE_NAME, where={"bot_id": bot_id}, type_=CounterDB)


def insert_counter(bot_id: int, name: str) -> Result[int]:
    return PROGRAMM_PARTS.database.insert(TABLE_NAME, {"bot_id": bot_id, "name": name})


def update_counter(bot_id: int, name: str, data: dict[str, Any]) -> Result[None]:
    return PROGRAMM_PARTS.database.update(TABLE_NAME, where={"bot_id": bot_id, "name": name}, data=data)


def delete_counter(bot_id: int, name: str) -> Result[None]:
    return PROGRAMM_PARTS.database.delete(TABLE_NAME, where={"bot_id": bot_id, "name": name})
