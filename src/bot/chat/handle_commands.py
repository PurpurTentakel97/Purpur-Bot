from typing import Optional

from bot.chat.types.message import ChatMessage
from bot.chat.types.message_response import ChatMessageResponse
from bot.core.types.permission_level import PermissionLevel


def handle_command(message: ChatMessage) -> Optional[ChatMessageResponse]:
    parts = message.text.strip().split(" ")

    if message.sender_permission_level.is_permitted(PermissionLevel.SPECIAL_USER):
        match parts:
            case ["!command", "add", _command_name, *msg]:
                command_message = " ".join(msg)
                if not command_message:
                    return message.to_response_message("There was no message provided after the command name.")

            case ["!command", "edit", _command_name, *msg]:
                command_message = " ".join(msg)
                if not command_message:
                    return message.to_response_message("There was no message provided after the command name.")

            case ["!command", "remove", _command_name, *_]:
                pass

            case ["!command", *_]:
                return message.to_response_message(
                    "Invalid command format. Use '!command add|edit|remove <command_name> <command_message>'"
                )

            case _:
                pass

    match parts:
        case ["!commands", *_]:
            pass
        case _:
            pass

    return message.to_response_message("TODO: Implement command handling.")
