from typing import Optional

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.database.types.base_command import BasicCommandDB

TABLE_NAME = "basic_commands"


def select_commands_by_bot_id(bot_id: int) -> list[BasicCommandDB]:
    return PROGRAMM_PARTS.database.select_all(table_name=TABLE_NAME, where={"bot_id": bot_id}, type_=BasicCommandDB)


def select_command(bot_id: int, command_name: str) -> Optional[BasicCommandDB]:
    return PROGRAMM_PARTS.database.select_one(
        table_name=TABLE_NAME, where={"bot_id": bot_id, "command": command_name}, type_=BasicCommandDB
    )


def insert_command(bot_id: int, command_name: str, command_message: str) -> Optional[int]:
    return PROGRAMM_PARTS.database.insert(
        table_name=TABLE_NAME, data={"bot_id": bot_id, "command": command_name, "message": command_message}
    )


def update_command_message(bot_id: int, command_name: str, command_message: str) -> bool:
    return PROGRAMM_PARTS.database.update(
        table_name=TABLE_NAME, where={"bot_id": bot_id, "command": command_name}, data={"message": command_message}
    )


def update_command_name(bot_id: int, old_command_name: str, new_command_name: str) -> bool:
    return PROGRAMM_PARTS.database.update(
        table_name=TABLE_NAME, where={"bot_id": bot_id, "command": old_command_name}, data={"command": new_command_name}
    )


def delete_command(bot_id: int, command_name: str) -> bool:
    return PROGRAMM_PARTS.database.delete(table_name=TABLE_NAME, where={"bot_id": bot_id, "command": command_name})
