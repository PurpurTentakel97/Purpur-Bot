from typing import Optional

from bot.database.commands import delete_command
from bot.database.commands import edit_command_message
from bot.database.commands import get_commands_by_bot_id
from bot.database.commands import lookup_command
from bot.database.commands import save_command
from bot.types.chat.message import ChatMessage
from bot.types.chat.message_response import ChatMessageResponse


def add_command(message: ChatMessage, command_name: str, command_message: str) -> ChatMessageResponse:
    command = lookup_command(message.id_, command_name.lstrip("!"))
    if command is not None:
        return ChatMessageResponse(
            f"Command '!{command_name}' already exists.",
            message.sender_chat,
            message.original_message,
            message.meta_data,
        )

    result = save_command(bot_id=message.id_, command_name=command_name, command_message=command_message)

    if not result:
        return ChatMessageResponse(
            f"Error add command '!{command_name}'", message.sender_chat, message.original_message, message.meta_data
        )

    return ChatMessageResponse(
        f"Command '!{command_name}' added successfully.",
        message.sender_chat,
        message.original_message,
        message.meta_data,
    )


def edit_command(message: ChatMessage, command_name: str, command_message: str) -> ChatMessageResponse:
    result = edit_command_message(message.id_, command_name.lstrip("!"), command_message)

    if not result:
        return ChatMessageResponse(
            f"Error editing command: '!{command_name}'",
            message.sender_chat,
            message.original_message,
            message.meta_data,
        )

    return ChatMessageResponse(
        f"Command '!{command_name}' edited successfully.",
        message.sender_chat,
        message.original_message,
        message.meta_data,
    )


def remove_command(message: ChatMessage, command_name: str) -> ChatMessageResponse:
    result = delete_command(message.id_, command_name.lstrip("!"))

    if not result:
        return ChatMessageResponse(
            f"Error removing command: '!{command_name}'",
            message.sender_chat,
            message.original_message,
            message.meta_data,
        )

    return ChatMessageResponse(
        f"Command '!{command_name}' removed successfully.",
        message.sender_chat,
        message.original_message,
        message.meta_data,
    )


def try_lookup_command(message: ChatMessage, command_name: str) -> Optional[ChatMessageResponse]:
    result = lookup_command(message.id_, command_name.lstrip("!"))

    if result is None:
        return None

    return ChatMessageResponse(result.message, message.sender_chat, message.original_message, message.meta_data)


def lookup_all_commands(message: ChatMessage) -> ChatMessageResponse:
    commands = get_commands_by_bot_id(message.id_)

    if not commands:
        return ChatMessageResponse(
            "No commands found.", message.sender_chat, message.original_message, message.meta_data
        )

    command_names = [f"!{x.command}" for x in commands]
    commands_text = ", ".join(command_names)

    return ChatMessageResponse(
        f"Commands: {commands_text}", message.sender_chat, message.original_message, message.meta_data
    )
