from typing import Any

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.database.types.base_command import BasicCommandDB

TABLE_NAME = "basic_commands"
FIELD_COMMAND = "command"
FIELD_MESSAGE = "message"


def select_commands_by_bot_id(bot_id: int) -> Result[list[BasicCommandDB]]:
    return PROGRAMM_PARTS.database.select_all(table_name=TABLE_NAME, where={"bot_id": bot_id}, type_=BasicCommandDB)


def select_command(bot_id: int, command_name: str) -> Result[BasicCommandDB]:
    return PROGRAMM_PARTS.database.select_one(
        table_name=TABLE_NAME, where={"bot_id": bot_id, "command": command_name}, type_=BasicCommandDB
    )


def insert_command(bot_id: int, command_name: str, command_message: str) -> Result[BasicCommandDB]:
    result = PROGRAMM_PARTS.database.insert(
        table_name=TABLE_NAME, data={"bot_id": bot_id, "command": command_name, "message": command_message}
    )

    if result.state.fail:
        return result.cast_to(BasicCommandDB)

    return select_command(bot_id, command_name)


def update_command(bot_id: int, command_name: str, data: dict[str, Any]) -> Result[BasicCommandDB]:
    result = PROGRAMM_PARTS.database.update(
        table_name=TABLE_NAME, where={"bot_id": bot_id, "command": command_name}, data=data
    )

    if result.state.fail:
        return result.cast_to(BasicCommandDB)

    return select_command(bot_id, command_name)


def delete_command(bot_id: int, command_name: str) -> Result[None]:
    return PROGRAMM_PARTS.database.delete(table_name=TABLE_NAME, where={"bot_id": bot_id, "command": command_name})
