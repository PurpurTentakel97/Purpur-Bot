from typing import Optional

from bot.database.types import BasicCommand
from bot.types.programm_parts import PROGRAMM_PARTS

TABLE_NAME = "basic_commands"


def get_commands_by_bot_id(bot_id: int) -> list[BasicCommand]:
    return PROGRAMM_PARTS.database.find_all(table_name=TABLE_NAME, where={"bot_id": bot_id}, type_=BasicCommand)


def lookup_command(bot_id: int, command_name: str) -> Optional[BasicCommand]:
    return PROGRAMM_PARTS.database.find_one(
        table_name=TABLE_NAME, where={"bot_id": bot_id, "command": command_name}, type_=BasicCommand
    )


def save_command(bot_id: int, command_name: str, command_message: str) -> bool:
    return PROGRAMM_PARTS.database.save(
        table_name=TABLE_NAME, data={"bot_id": bot_id, "command": command_name, "message": command_message}
    )


def edit_command_message(bot_id: int, command_name: str, command_message: str) -> bool:
    return PROGRAMM_PARTS.database.update(
        table_name=TABLE_NAME, where={"bot_id": bot_id, "command": command_name}, data={"message": command_message}
    )


def edit_command_name(bot_id: int, old_command_name: str, new_command_name: str) -> bool:
    return PROGRAMM_PARTS.database.update(
        table_name=TABLE_NAME, where={"bot_id": bot_id, "command": old_command_name}, data={"command": new_command_name}
    )


def delete_command(bot_id: int, command_name: str) -> bool:
    return PROGRAMM_PARTS.database.delete(table_name=TABLE_NAME, where={"bot_id": bot_id, "command": command_name})
