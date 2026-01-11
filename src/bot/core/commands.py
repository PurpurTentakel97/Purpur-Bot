from bot.core.helpers.string import has_whitespace
from bot.core.helpers.string import identifier_for_db
from bot.core.helpers.string import strip_for_db
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.commands import FIELD_COMMAND
from bot.database.commands import FIELD_MESSAGE
from bot.database.commands import delete_command as delete_command_db
from bot.database.commands import insert_command as insert_command_db
from bot.database.commands import select_commands_by_bot_id as select_commands_by_bot_id_db
from bot.database.commands import update_command as update_command_db
from bot.database.types.base_command import BasicCommandDB


def get_commands_by_bot_id(bot_id: int) -> Result[list[BasicCommandDB]]:
    return select_commands_by_bot_id_db(bot_id)


def save_command(bot_id: int, name: str, message: str) -> Result[BasicCommandDB]:
    name_db = identifier_for_db(name)

    if has_whitespace(name_db):
        return Result(ResultState.WHITESPACE_ERROR, None)

    return insert_command_db(bot_id, identifier_for_db(name), strip_for_db(message))


def update_command_message(bot_id: int, name: str, message: str) -> Result[BasicCommandDB]:
    return update_command_db(bot_id, identifier_for_db(name), {FIELD_MESSAGE: strip_for_db(message)})


def update_command_name(bot_id: int, old_name: str, new_name: str) -> Result[BasicCommandDB]:
    return update_command_db(bot_id, identifier_for_db(old_name), {FIELD_COMMAND: identifier_for_db(new_name)})


def delete_command(bot_id: int, name: str) -> Result[None]:
    return delete_command_db(bot_id, identifier_for_db(name))
