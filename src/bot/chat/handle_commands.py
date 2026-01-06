from typing import Optional

from bot.chat.types.message import ChatMessage
from bot.chat.types.message_response import ChatMessageResponse
from bot.core.commands import add_command
from bot.core.commands import edit_command
from bot.core.commands import lookup_all_commands
from bot.core.commands import remove_command
from bot.core.commands import try_lookup_command
from bot.core.types.permission_level import PermissionLevel


def handle_command(message: ChatMessage) -> Optional[ChatMessageResponse]:
    parts = message.text.strip().split(" ")

    if message.sender_permission_level.is_permitted(PermissionLevel.SPECIAL_USER):
        match parts:
            case ["!command", "add", command_name, *msg]:
                command_message = " ".join(msg)
                if not command_message:
                    return ChatMessageResponse(
                        "There was no message provided after the command name.",
                        message.sender_chat,
                        message.original_message,
                        message.meta_data,
                    )
                return add_command(message, command_name, command_message)

            case ["!command", "edit", command_name, *msg]:
                command_message = " ".join(msg)
                if not command_message:
                    return ChatMessageResponse(
                        "There was no message provided after the command name.",
                        message.sender_chat,
                        message.original_message,
                        message.meta_data,
                    )
                return edit_command(message, command_name, command_message)

            case ["!command", "remove", command_name, *_]:
                return remove_command(message, command_name)

            case ["!command", *_]:
                return ChatMessageResponse(
                    "Invalid command format. Use '!command add|edit|remove <command_name> <command_message>'",
                    message.sender_chat,
                    message.original_message,
                    message.meta_data,
                )
            case _:
                pass

    match parts:
        case ["!commands", *_]:
            return lookup_all_commands(message)
        case _:
            pass

    return try_lookup_command(message, parts[0])
