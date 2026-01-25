from typing import Any

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.database.types.base_command import BasicCommandDB
from bot.database.types.fields import FIELD_BASIC_COMMAND_COMMAND
from bot.database.types.fields import FIELD_BASIC_COMMAND_MESSAGE
from bot.database.types.fields import FIELD_BOT_ID
from bot.database.types.fields import FIELD_ID
from bot.database.types.fields import TABLE_BASIC_COMMANDS_NAME


def select_commands_by_bot_id(bot_id: int) -> Result[list[BasicCommandDB]]:
    return PROGRAMM_PARTS.database.select_all(
        table_name=TABLE_BASIC_COMMANDS_NAME, where={FIELD_BOT_ID: bot_id}, type_=BasicCommandDB
    )


def select_command_by_id(command_id: int) -> Result[BasicCommandDB]:
    return PROGRAMM_PARTS.database.select_one(
        table_name=TABLE_BASIC_COMMANDS_NAME, where={FIELD_ID: command_id}, type_=BasicCommandDB
    )


def select_command(bot_id: int, command_name: str) -> Result[BasicCommandDB]:
    return PROGRAMM_PARTS.database.select_one(
        table_name=TABLE_BASIC_COMMANDS_NAME,
        where={FIELD_BOT_ID: bot_id, FIELD_BASIC_COMMAND_COMMAND: command_name},
        type_=BasicCommandDB,
    )


def insert_command(bot_id: int, command_name: str, command_message: str) -> Result[BasicCommandDB]:
    result = PROGRAMM_PARTS.database.insert(
        table_name=TABLE_BASIC_COMMANDS_NAME,
        data={
            FIELD_BOT_ID: bot_id,
            FIELD_BASIC_COMMAND_COMMAND: command_name,
            FIELD_BASIC_COMMAND_MESSAGE: command_message,
        },
    )

    if result.state.fail:
        return result.cast_to(BasicCommandDB)

    return select_command(bot_id, command_name)


def update_command_by_id(command_id: int, data: dict[str, Any]) -> Result[BasicCommandDB]:
    result = PROGRAMM_PARTS.database.update(
        table_name=TABLE_BASIC_COMMANDS_NAME, where={FIELD_ID: command_id}, data=data
    )

    if result.state.fail:
        return result.cast_to(BasicCommandDB)

    return select_command_by_id(command_id)


def update_command(bot_id: int, command_name: str, data: dict[str, Any]) -> Result[BasicCommandDB]:
    result = PROGRAMM_PARTS.database.update(
        table_name=TABLE_BASIC_COMMANDS_NAME,
        where={FIELD_BOT_ID: bot_id, FIELD_BASIC_COMMAND_COMMAND: command_name},
        data=data,
    )

    if result.state.fail:
        return result.cast_to(BasicCommandDB)

    new_command_name = command_name
    if FIELD_BASIC_COMMAND_COMMAND in data:
        new_command_name = data[FIELD_BASIC_COMMAND_COMMAND]
    return select_command(bot_id, new_command_name)


def delete_command_by_id(command_id: int) -> Result[None]:
    return PROGRAMM_PARTS.database.delete(table_name=TABLE_BASIC_COMMANDS_NAME, where={FIELD_ID: command_id})


def delete_command(bot_id: int, command_name: str) -> Result[None]:
    return PROGRAMM_PARTS.database.delete(
        table_name=TABLE_BASIC_COMMANDS_NAME, where={FIELD_BOT_ID: bot_id, FIELD_BASIC_COMMAND_COMMAND: command_name}
    )
