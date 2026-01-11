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


def insert_counter(bot_id: int, name: str) -> Result[CounterDB]:
    result = PROGRAMM_PARTS.database.insert(TABLE_NAME, {"bot_id": bot_id, "name": name, "count": 0})

    if result.state.fail:
        return result.cast_to(CounterDB)

    return select_counter(bot_id, name)


def update_counter_name(bot_id: int, old_name: str, new_name: str) -> Result[CounterDB]:
    result = PROGRAMM_PARTS.database.update(
        TABLE_NAME, where={"bot_id": bot_id, "name": old_name}, data={"name": new_name}
    )

    if result.state.fail:
        return result.cast_to(CounterDB)

    return select_counter(bot_id, new_name)


def update_counter(bot_id: int, name: str, data: dict[str, Any]) -> Result[CounterDB]:
    result = PROGRAMM_PARTS.database.update(TABLE_NAME, where={"bot_id": bot_id, "name": name}, data=data)

    if result.state.fail:
        return result.cast_to(CounterDB)

    return select_counter(bot_id, name)


def delete_counter(bot_id: int, name: str) -> Result[None]:
    return PROGRAMM_PARTS.database.delete(TABLE_NAME, where={"bot_id": bot_id, "name": name})
