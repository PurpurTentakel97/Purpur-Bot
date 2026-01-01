from typing import Optional

from bot.database.database import DatabaseDeleteData
from bot.database.database import DatabaseGetData
from bot.database.database import DatabaseSaveData
from bot.database.database import DatabaseUpdateData
from bot.types.chat_message import ChatMessage
from bot.types.database_result import DatabaseResult
from bot.types.programm_parts import PROGRAMM_PARTS
from bot.types.response_message import ResponseMessage

TABLE_NAME = "basic_commands"


def add_command(message: ChatMessage, command_name: str, command_message: str) -> ResponseMessage:
    if try_lookup_command(message, command_name) is not None:
        return ResponseMessage(
            f"Command '!{command_name}' already exists.",
            message.sender_chat,
            message.original_message,
            message.meta_data,
        )

    data = DatabaseSaveData(
        table_name=TABLE_NAME, data={"id": message.id_, "name": command_name, "message": command_message}
    )

    result = PROGRAMM_PARTS.database.save(data)
    if not DatabaseResult.is_success(result):
        return ResponseMessage(
            f"Error add command '!{command_name}'", message.sender_chat, message.original_message, message.meta_data
        )

    return ResponseMessage(
        f"Command '!{command_name}' added successfully.",
        message.sender_chat,
        message.original_message,
        message.meta_data,
    )


def edit_command(message: ChatMessage, command_name: str, command_message: str) -> ResponseMessage:
    data = DatabaseUpdateData(
        table_name=TABLE_NAME, data={"message": command_message}, where={"id": message.id_, "name": command_name}
    )

    result = PROGRAMM_PARTS.database.update(data)
    if not DatabaseResult.is_success(result):
        if result == DatabaseResult.NO_DATA_EDITED:
            return ResponseMessage(
                f"Command '!{command_name}' does not exist.",
                message.sender_chat,
                message.original_message,
                message.meta_data,
            )
        return ResponseMessage(
            f"Error editing command: '!{command_name}'",
            message.sender_chat,
            message.original_message,
            message.meta_data,
        )

    return ResponseMessage(
        f"Command '!{command_name}' edited successfully.",
        message.sender_chat,
        message.original_message,
        message.meta_data,
    )


def remove_command(message: ChatMessage, command_name: str) -> ResponseMessage:
    data = DatabaseDeleteData(table_name=TABLE_NAME, where={"id": message.id_, "name": command_name})

    result = PROGRAMM_PARTS.database.delete(data)
    if not DatabaseResult.is_success(result):
        if result == DatabaseResult.NO_DATA_EDITED:
            return ResponseMessage(
                f"Command '!{command_name}' does not exist.",
                message.sender_chat,
                message.original_message,
                message.meta_data,
            )
        return ResponseMessage(
            f"Error removing command: '!{command_name}'",
            message.sender_chat,
            message.original_message,
            message.meta_data,
        )

    return ResponseMessage(
        f"Command '!{command_name}' removed successfully.",
        message.sender_chat,
        message.original_message,
        message.meta_data,
    )


def try_lookup_command(message: ChatMessage, command_name: str) -> Optional[ResponseMessage]:
    data = DatabaseGetData(
        table_name=TABLE_NAME, keys=["message"], where={"id": message.id_, "name": command_name.lstrip("!")}
    )
    result = PROGRAMM_PARTS.database.get_single(data, "")

    if not DatabaseResult.is_success(result.result):
        return None
    if result.data is None:
        return None

    return ResponseMessage(result.data, message.sender_chat, message.original_message, message.meta_data)


def lookup_all_commands(message: ChatMessage) -> ResponseMessage:
    return ResponseMessage(
        "TODO: display_all_commands", message.sender_chat, message.original_message, message.meta_data
    )
