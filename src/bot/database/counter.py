from typing import Optional

from bot.database.types import Counter
from bot.types.programm_parts import PROGRAMM_PARTS

TABLE_NAME = "counter"


def get_counter(bot_id: int, name: str) -> Optional[Counter]:
    return PROGRAMM_PARTS.database.find_one(TABLE_NAME, where={"bot_id": bot_id, "name": name}, type_=Counter)


def get_counter_by_bot_id(bot_id: int) -> list[Counter]:
    return PROGRAMM_PARTS.database.find_all(TABLE_NAME, where={"bot_id": bot_id}, type_=Counter)


def save_counter(bot_id: int, name: str) -> bool:
    return PROGRAMM_PARTS.database.save(TABLE_NAME, {"bot_id": bot_id, "name": name})


def increment_counter_by(bot_id: int, name: str, value: int) -> bool:
    counter = get_counter(bot_id, name)
    if counter is None:
        return False
    return PROGRAMM_PARTS.database.update(
        TABLE_NAME, where={"bot_id": bot_id, "name": name}, data={"value": counter.value + value}
    )


def decrement_counter_by(bot_id: int, name: str, value: int) -> bool:
    counter = get_counter(bot_id, name)
    if counter is None:
        return False

    if counter.value - value < 0:
        return PROGRAMM_PARTS.database.update(TABLE_NAME, where={"bot_id": bot_id, "name": name}, data={"value": 0})

    return PROGRAMM_PARTS.database.update(
        TABLE_NAME, where={"bot_id": bot_id, "name": name}, data={"value": counter.value - value}
    )


def reset_counter(bot_id: int, name: str) -> bool:
    return PROGRAMM_PARTS.database.update(TABLE_NAME, where={"bot_id": bot_id, "name": name}, data={"value": 0})


def delete_counter(bot_id: int, name: str) -> bool:
    return PROGRAMM_PARTS.database.delete(TABLE_NAME, where={"bot_id": bot_id, "name": name})
