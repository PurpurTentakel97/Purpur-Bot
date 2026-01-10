from bot.core.types.result import Result
from bot.database.counter import insert_counter as insert_counter_db
from bot.database.counter import update_counter as update_counter_db
from bot.database.counter import delete_counter as delete_counter_db
from bot.database.counter import FIELD_COUNTER, FIELD_NAME


def save_counter(bot_id: int, name: str) -> Result[int]:
    return insert_counter_db(bot_id, name)


def edit_counter_name(bot_id: int, old_name: str, new_name: str) -> Result[None]:
    return update_counter_db(bot_id, old_name, {FIELD_NAME: new_name})


def edit_counter_value(bot_id: int, name: str, value: int) -> Result[None]:
    return update_counter_db(bot_id, name, {FIELD_COUNTER: value})


def reset_counter(bot_id: int, name: str) -> Result[None]:
    return edit_counter_value(bot_id, name, 0)


def delete_counter(bot_id: int, name: str) -> Result[None]:
    return delete_counter_db(bot_id, name)
