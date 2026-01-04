from typing import Optional

from bot.database.types import BasicCommand
from bot.types.chat_message import ChatMessage
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

    result = PROGRAMM_PARTS.database.save(
        table_name=TABLE_NAME, data={"id": message.id_, "name": command_name, "message": command_message}
    )

    if not result:
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
    result = PROGRAMM_PARTS.database.update(
        table_name=TABLE_NAME,
        where={"id": message.id_, "name": command_name},
        data={"message": command_message},
    )
    if not result:
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
    result = PROGRAMM_PARTS.database.delete(table_name=TABLE_NAME, where={"id": message.id_, "name": command_name})
    if not result:
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
    result = PROGRAMM_PARTS.database.find_one(
        table_name=TABLE_NAME, where={"id": message.id_, "name": command_name.lstrip("!")}, type_=BasicCommand
    )

    if result is None:
        return None

    return ResponseMessage(result.message, message.sender_chat, message.original_message, message.meta_data)


def lookup_all_commands(message: ChatMessage) -> ResponseMessage:
    return ResponseMessage(
        "TODO: display_all_commands", message.sender_chat, message.original_message, message.meta_data
    )
