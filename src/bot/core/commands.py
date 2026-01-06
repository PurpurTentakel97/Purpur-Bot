from typing import Optional

from bot.database.commands import delete_command
from bot.database.commands import edit_command_message
from bot.database.commands import get_commands_by_bot_id
from bot.database.commands import lookup_command
from bot.database.commands import save_command
from bot.types.chat_message import ChatMessage
from bot.types.response_message import ResponseMessage


def add_command(message: ChatMessage, command_name: str, command_message: str) -> ResponseMessage:
    command = lookup_command(message.id_, command_name.lstrip("!"))
    if command is not None:
        return ResponseMessage(
            f"Command '!{command_name}' already exists.",
            message.sender_chat,
            message.original_message,
            message.meta_data,
        )

    result = save_command(bot_id=message.id_, command_name=command_name, command_message=command_message)

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
    result = edit_command_message(message.id_, command_name.lstrip("!"), command_message)

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
    result = delete_command(message.id_, command_name.lstrip("!"))

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
    result = lookup_command(message.id_, command_name.lstrip("!"))

    if result is None:
        return None

    return ResponseMessage(result.message, message.sender_chat, message.original_message, message.meta_data)


def lookup_all_commands(message: ChatMessage) -> ResponseMessage:
    commands = get_commands_by_bot_id(message.id_)

    if not commands:
        return ResponseMessage("No commands found.", message.sender_chat, message.original_message, message.meta_data)

    command_names = [f"!{x.command}" for x in commands]
    commands_text = ", ".join(command_names)

    return ResponseMessage(
        f"Commands: {commands_text}", message.sender_chat, message.original_message, message.meta_data
    )
