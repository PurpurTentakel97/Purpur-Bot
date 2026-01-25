from typing import Any

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.database.types.counter import CounterDB
from bot.database.types.fields import FIELD_BOT_ID
from bot.database.types.fields import FIELD_COUNTER_COUNT
from bot.database.types.fields import FIELD_COUNTER_NAME
from bot.database.types.fields import FIELD_ID
from bot.database.types.fields import TABLE_COUNTER_NAME


def select_counter(bot_id: int, name: str) -> Result[CounterDB]:
    return PROGRAMM_PARTS.database.select_one(
        TABLE_COUNTER_NAME, where={FIELD_BOT_ID: bot_id, FIELD_COUNTER_NAME: name}, type_=CounterDB
    )


def select_counter_by_id(counter_id: int) -> Result[CounterDB]:
    return PROGRAMM_PARTS.database.select_one(TABLE_COUNTER_NAME, where={FIELD_ID: counter_id}, type_=CounterDB)


def select_counter_by_bot_id(bot_id: int) -> Result[list[CounterDB]]:
    return PROGRAMM_PARTS.database.select_all(TABLE_COUNTER_NAME, where={FIELD_BOT_ID: bot_id}, type_=CounterDB)


def insert_counter(bot_id: int, name: str) -> Result[CounterDB]:
    result = PROGRAMM_PARTS.database.insert(
        TABLE_COUNTER_NAME, {FIELD_BOT_ID: bot_id, FIELD_COUNTER_NAME: name, FIELD_COUNTER_COUNT: 0}
    )

    if result.state.fail:
        return result.cast_to(CounterDB)

    return select_counter(bot_id, name)


def update_counter_by_id(counter_id: int, data: dict[str, Any]) -> Result[CounterDB]:
    result = PROGRAMM_PARTS.database.update(TABLE_COUNTER_NAME, where={FIELD_ID: counter_id}, data=data)

    if result.state.fail:
        return result.cast_to(CounterDB)

    return select_counter_by_id(counter_id)


def update_counter(bot_id: int, name: str, data: dict[str, Any]) -> Result[CounterDB]:
    result = PROGRAMM_PARTS.database.update(
        TABLE_COUNTER_NAME, where={FIELD_BOT_ID: bot_id, FIELD_COUNTER_NAME: name}, data=data
    )

    if result.state.fail:
        return result.cast_to(CounterDB)

    new_name = name
    if FIELD_COUNTER_NAME in data:
        new_name = data[FIELD_COUNTER_NAME]
    return select_counter(bot_id, new_name)


def delete_counter_by_id(counter_id: int) -> Result[None]:
    return PROGRAMM_PARTS.database.delete(TABLE_COUNTER_NAME, where={FIELD_ID: counter_id})


def delete_counter(bot_id: int, name: str) -> Result[None]:
    return PROGRAMM_PARTS.database.delete(TABLE_COUNTER_NAME, where={FIELD_BOT_ID: bot_id, FIELD_COUNTER_NAME: name})
