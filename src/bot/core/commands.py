from bot.core.helpers.string import has_whitespace
from bot.core.helpers.string import identifier_for_db
from bot.core.helpers.string import strip_for_db
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.commands import FIELD_COMMAND
from bot.database.commands import FIELD_MESSAGE
from bot.database.commands import delete_command as delete_command_db
from bot.database.commands import insert_command as insert_command_db
from bot.database.commands import select_command as select_command_db
from bot.database.commands import select_commands_by_bot_id as select_commands_by_bot_id_db
from bot.database.commands import update_command as update_command_db
from bot.database.types.base_command import BasicCommandDB


def _exists(bot_id: int, name: str) -> bool:
    return get_command(bot_id, name).value is not None


def get_commands_by_bot_id(bot_id: int) -> Result[list[BasicCommandDB]]:
    return select_commands_by_bot_id_db(bot_id)


def get_command(bot_id: int, name: str) -> Result[BasicCommandDB]:
    return select_command_db(bot_id, identifier_for_db(name))


def save_command(bot_id: int, name: str, message: str) -> Result[BasicCommandDB]:
    name_db = identifier_for_db(name)
    message_db = strip_for_db(message)

    if not name_db:
        return Result(ResultState.EMPTY_NAME, None)

    if not message_db:
        return Result(ResultState.EMPTY_MESSAGE, None)

    if has_whitespace(name_db):
        return Result(ResultState.WHITESPACE_ERROR, None)

    if _exists(bot_id, name_db):
        return Result(ResultState.ALREADY_EXISTS, None)

    return insert_command_db(bot_id, identifier_for_db(name), message_db)


def update_command_message(bot_id: int, name: str, message: str) -> Result[BasicCommandDB]:
    message_db = strip_for_db(message)

    if not message_db:
        return Result(ResultState.EMPTY_MESSAGE, None)

    return update_command_db(bot_id, identifier_for_db(name), {FIELD_MESSAGE: message_db})


def update_command_name(bot_id: int, old_name: str, new_name: str) -> Result[BasicCommandDB]:
    new_name_db = identifier_for_db(new_name)
    old_name_db = identifier_for_db(old_name)

    if not new_name_db:
        return Result(ResultState.EMPTY_NAME, None)

    if has_whitespace(new_name_db):
        return Result(ResultState.WHITESPACE_ERROR, None)

    if _exists(bot_id, new_name_db):
        return Result(ResultState.ALREADY_EXISTS, None)

    return update_command_db(bot_id, old_name_db, {FIELD_COMMAND: new_name_db})


def delete_command(bot_id: int, name: str) -> Result[None]:
    return delete_command_db(bot_id, identifier_for_db(name))
