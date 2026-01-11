from typing import Optional

from bot.chat.types.message import ChatMessage
from bot.chat.types.message_response import ChatMessageResponse
from bot.core.commands import delete_command as delete_command_core
from bot.core.commands import get_command as get_command_core
from bot.core.commands import get_commands_by_bot_id as get_commands_by_bot_id_core
from bot.core.commands import save_command as save_command_core
from bot.core.commands import update_command_message as update_command_message_core
from bot.core.commands import update_command_name as update_command_name_core
from bot.core.types.permission_level import PermissionLevel
from bot.core.types.result import ResultState


def _result_lookup(state: ResultState) -> str:
    match state:
        case ResultState.WHITESPACE_ERROR:
            return "the identifier contains whitespace."
        case ResultState.ALREADY_EXISTS:
            return "the identifier already exists."
        case ResultState.EMPTY_NAME:
            return "the identifier is empty."
        case ResultState.EMPTY_MESSAGE:
            return "the message is empty."
        case _:
            return "internal error"


def handle_command(message: ChatMessage) -> Optional[ChatMessageResponse]:
    parts = message.text.strip().split(" ")

    if message.sender_permission_level.is_permitted(PermissionLevel.SPECIAL_USER):
        match parts:
            case ["!command", "add", command_name, *msg]:
                command_message = " ".join(msg)
                result = save_command_core(message.bot_id, command_name, " ".join(msg))

                if result.state.success and result.value is not None:
                    return message.to_response_message(f"Command '{result.value.command}' saved successfully.")

                return message.to_response_message(f"Failed to save command: {_result_lookup(result.state)}")

            case ["!command", "edit_message", command_name, *msg]:
                command_message = " ".join(msg)
                result = update_command_message_core(message.bot_id, command_name, command_message)

                if result.state.success and result.value is not None:
                    return message.to_response_message(f"Command '{result.value.command}' edited successfully.")

                return message.to_response_message(f"Failed to edit command message: {_result_lookup(result.state)}")

            case ["!command", "edit_name", old_command_name, new_command_name, *_]:
                result = update_command_name_core(message.bot_id, old_command_name, new_command_name)

                if result.state.success and result.value is not None:
                    return message.to_response_message(
                        f"Command '{old_command_name.strip().lower()}'"
                        + f" renamed successfully to '{result.value.command}'."
                    )

                return message.to_response_message(f"Failed to rename command: {_result_lookup(result.state)}")

            case ["!command", "remove", command_name, *_]:
                result = delete_command_core(message.bot_id, command_name)
                if result.state.success:
                    return message.to_response_message(
                        f"Command '{command_name.strip().lower()}' deleted successfully."
                    )

                return message.to_response_message(f"Failed to delete command: {_result_lookup(result.state)}")

            case ["!command", *_]:
                return message.to_response_message(
                    "Invalid command format. Use '!command add|edit|remove <command_name> <command_message>'"
                )

            case _:
                pass

    match parts:
        case ["!commands", *_]:
            result = get_commands_by_bot_id_core(message.bot_id)

            if result.state.success and result.value is not None:
                return message.to_response_message(
                    f"Commands: {', '.join([message.command for message in result.value])}"
                )

            return message.to_response_message("No commands found.")

        case _:
            pass

    if len(parts) < 1:
        return None

    result = get_command_core(message.bot_id, parts[0].lstrip("!"))
    if result.state.success and result.value is not None:
        return message.to_response_message(result.value.message)

    return None
