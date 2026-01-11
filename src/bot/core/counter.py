from bot.core.helpers.string import has_whitespace
from bot.core.helpers.string import identifier_for_db
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.counter import FIELD_COUNTER
from bot.database.counter import FIELD_NAME
from bot.database.counter import delete_counter as delete_counter_db
from bot.database.counter import insert_counter as insert_counter_db
from bot.database.counter import select_counter
from bot.database.counter import update_counter as update_counter_db
from bot.database.types.counter import CounterDB


def get_counter(bot_id: int, name: str) -> Result[CounterDB]:
    return select_counter(bot_id, identifier_for_db(name))


def save_counter(bot_id: int, name: str) -> Result[CounterDB]:
    name_db = identifier_for_db(name)

    if has_whitespace(name_db):
        return Result(ResultState.WHITESPACE_ERROR, None)

    return insert_counter_db(bot_id, name_db)


def edit_counter_name(bot_id: int, old_name: str, new_name: str) -> Result[CounterDB]:
    return update_counter_db(bot_id, identifier_for_db(old_name), {FIELD_NAME: identifier_for_db(new_name)})


def edit_counter_value(bot_id: int, name: str, value: int) -> Result[CounterDB]:
    return update_counter_db(bot_id, identifier_for_db(name), {FIELD_COUNTER: value})


def reset_counter(bot_id: int, name: str) -> Result[CounterDB]:
    return edit_counter_value(bot_id, identifier_for_db(name), 0)


def increment_counter_by(bot_id: int, name: str, offset: int) -> Result[CounterDB]:
    name_db = identifier_for_db(name)
    get_result = get_counter(bot_id, name_db)

    if not get_result.state.is_success() or get_result.value is None:
        return get_result

    new_value = get_result.value.count + offset

    update_result = edit_counter_value(bot_id, name_db, new_value)

    if not update_result.state.is_success():
        return update_result.cast_to(CounterDB, None)

    get_result.value.count = new_value
    return update_result.cast_to(CounterDB, get_result.value)


def increment_counter(bot_id: int, name: str) -> Result[CounterDB]:
    return increment_counter_by(bot_id, name, 1)  # name will be handled in increment_counter_by


def decrement_counter_by(bot_id: int, name: str, offset: int) -> Result[CounterDB]:
    return increment_counter_by(bot_id, name, -offset)  # name will be handled in increment_counter_by


def decrement_counter(bot_id: int, name: str) -> Result[CounterDB]:
    return increment_counter_by(bot_id, name, -1)  # name will be handled in increment_counter_by


def delete_counter(bot_id: int, name: str) -> Result[None]:
    return delete_counter_db(bot_id, identifier_for_db(name))
