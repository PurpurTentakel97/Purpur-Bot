from typing import Optional

from bot.database.commands import add_command
from bot.database.commands import edit_command
from bot.database.commands import lookup_all_commands
from bot.database.commands import remove_command
from bot.database.commands import try_lookup_command
from bot.types.chat_message import ChatMessage
from bot.types.permission_level import PermissionLevel
from bot.types.response_message import ResponseMessage


def handle_command(message: ChatMessage) -> Optional[ResponseMessage]:
    parts = message.text.strip().split(" ")

    if (
        message.sender_permission_level == PermissionLevel.MODERATOR
        or message.sender_permission_level == PermissionLevel.ADMIN
    ):
        match parts:
            case ["!command", "add", command_name, *msg]:
                command_message = " ".join(msg)
                if not command_message:
                    return ResponseMessage(
                        "There was no message provided after the command name.",
                        message.sender_chat,
                        message.original_message,
                        message.meta_data,
                    )
                return add_command(message, command_name, command_message)

            case ["!command", "edit", command_name, *msg]:
                command_message = " ".join(msg)
                if not command_message:
                    return ResponseMessage(
                        "There was no message provided after the command name.",
                        message.sender_chat,
                        message.original_message,
                        message.meta_data,
                    )
                return edit_command(message, command_name, command_message)

            case ["!command", "remove", command_name, *_]:
                return remove_command(message, command_name)

            case ["!command", *_]:
                return ResponseMessage(
                    "Invalid command format. Use '!command add|edit|remove <command_name> <command_message>'",
                    message.sender_chat,
                    message.original_message,
                    message.meta_data,
                )
            case _:
                pass

    match parts:
        case ["!commands", *_]:
            lookup_all_commands(message)
        case _:
            pass

    return try_lookup_command(message, parts[0])
