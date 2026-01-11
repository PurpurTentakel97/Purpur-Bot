from typing import Optional

from bot.chat.types.message import ChatMessage
from bot.chat.types.message_response import ChatMessageResponse
from bot.core.commands import delete_command as delete_command_core
from bot.core.commands import get_command_with_counter as get_command_core
from bot.core.commands import get_commands_by_bot_id as get_commands_by_bot_id_core
from bot.core.commands import save_command as save_command_core
from bot.core.commands import update_command_message as update_command_message_core
from bot.core.commands import update_command_name as update_command_name_core
from bot.core.counter import decrement_counter as decrement_counter_core
from bot.core.counter import decrement_counter_by as decrement_counter_by_core
from bot.core.counter import delete_counter as delete_counter_core
from bot.core.counter import edit_counter_name as edit_counter_name_core
from bot.core.counter import edit_counter_value as edit_counter_value_core
from bot.core.counter import get_counter as get_counter_core
from bot.core.counter import increment_counter as increment_counter_core
from bot.core.counter import increment_counter_by as increment_counter_by_core
from bot.core.counter import reset_counter as reset_counter_core
from bot.core.counter import save_counter as save_counter_core
from bot.core.types.permission_level import PermissionLevel
from bot.core.types.result import ResultState


def _to_int(value: str) -> Optional[int]:
    try:
        return int(value)
    except ValueError:
        return None


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
        case ResultState.SILL_IN_USE:
            return "the identifier is still in use."
        case ResultState.NO_DATA:
            return "unknown identifier."
        case _:
            return "internal error"


def handle_command(message: ChatMessage) -> Optional[ChatMessageResponse]:
    parts = message.text.strip().split(" ")

    if message.sender_permission_level.is_permitted(PermissionLevel.SPECIAL_USER):
        match parts:
            # command
            case ["!command", "add", command_name, *msg]:
                command_message = " ".join(msg)
                result = save_command_core(message.bot_id, command_name, command_message)
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

            # counter
            case ["!counter", "add", counter_name, *_]:
                result = save_counter_core(message.bot_id, counter_name)
                if result.state.success and result.value is not None:
                    return message.to_response_message(f"Counter '{result.value.name}' created successfully.")
                return message.to_response_message(f"Failed to create counter: {_result_lookup(result.state)}")

            case ["!counter", "reset", counter_name, *_]:
                result = reset_counter_core(message.bot_id, counter_name)
                if result.state.success and result.value is not None:
                    return message.to_response_message(f"Counter '{result.value.name}' reset successfully.")
                return message.to_response_message(f"Failed to reset counter: {_result_lookup(result.state)}")

            case ["!counter", "remove", counter_name, *_]:
                result = delete_counter_core(message.bot_id, counter_name)
                if result.state.success:
                    return message.to_response_message(
                        f"Counter '{counter_name.strip().lower()}' deleted successfully."
                    )
                return message.to_response_message(f"Failed to delete counter: {_result_lookup(result.state)}")

            case ["!counter", "show", counter_name, *_]:
                result = get_counter_core(message.bot_id, counter_name)
                if result.state.success and result.value is not None:
                    return message.to_response_message(f"Counter '{result.value.name}': {result.value.count}")
                return message.to_response_message(f"Failed to show counter: {_result_lookup(result.state)}")

            case ["!counter", "increment", counter_name, *_]:
                result = increment_counter_core(message.bot_id, counter_name)
                if result.state.success and result.value is not None:
                    return message.to_response_message(
                        f"Counter '{result.value.name}' incremented successfully to '{result.value.count}'."
                    )
                return message.to_response_message(f"Failed to increment counter: {_result_lookup(result.state)}")

            case ["!counter", "increment_by", counter_name, value, *_]:
                v = _to_int(value)
                if v is None:
                    return message.to_response_message("Invalid value. Must be a number.")

                result = increment_counter_by_core(message.bot_id, counter_name, v)
                if result.state.success and result.value is not None:
                    return message.to_response_message(
                        f"Counter '{result.value.name}' incremented by '{v}' successfully to '{result.value.count}'."
                    )
                return message.to_response_message(f"Failed to increment counter: {_result_lookup(result.state)}")

            case ["!counter", "decrement", counter_name, *_]:
                result = decrement_counter_core(message.bot_id, counter_name)
                if result.state.success and result.value is not None:
                    return message.to_response_message(
                        f"Counter '{result.value.name}' decremented successfully to '{result.value.count}'."
                    )
                return message.to_response_message(f"Failed to decrement counter: {_result_lookup(result.state)}")

            case ["!counter", "decrement_by", counter_name, value, *_]:
                v = _to_int(value)
                if v is None:
                    return message.to_response_message("Invalid value. Must be a number.")

                result = decrement_counter_by_core(message.bot_id, counter_name, v)
                if result.state.success and result.value is not None:
                    return message.to_response_message(
                        f"Counter '{result.value.name}' decremented by '{v}' successfully to '{result.value.count}'."
                    )
                return message.to_response_message(f"Failed to decrement counter: {_result_lookup(result.state)}")

            case ["!counter", "set_count", counter_name, value, *_]:
                v = _to_int(value)
                if v is None:
                    return message.to_response_message("Invalid value. Must be a number.")

                result = edit_counter_value_core(message.bot_id, counter_name, v)
                if result.state.success and result.value is not None:
                    return message.to_response_message(f"Counter '{result.value.name}' set to '{result.value.count}'.")
                return message.to_response_message(f"Failed to set counter value: {_result_lookup(result.state)}")

            case ["!counter", "set_name", counter_name, new_name, *_]:
                result = edit_counter_name_core(message.bot_id, counter_name, new_name)
                if result.state.success and result.value is not None:
                    return message.to_response_message(
                        f"Counter '{result.value.name}' renamed to '{result.value.name}'."
                    )
                return message.to_response_message(f"Failed to rename counter: {_result_lookup(result.state)}")

            case ["!counter", *_]:
                return message.to_response_message(
                    "Invalid command format. Use '!counter"
                    + " add|reset|remove|show|increment|decrement|set_name|set_count <counter_name> <new_value>'"
                )
            case _:
                pass

    match parts:
        case ["!commands", *_]:
            result = get_commands_by_bot_id_core(message.bot_id)

            if result.state.success and result.value is not None:
                commands = (
                    ", ".join([message.command for message in result.value])
                    if len(result.value) > 0
                    else "(no commands)"
                )
                return message.to_response_message(f"Commands: {commands}")

            return message.to_response_message("No commands found.")

        case _:
            pass

    if len(parts) < 1:
        return None

    result = get_command_core(message.bot_id, parts[0].lstrip("!"))
    if result.state.success and result.value is not None:
        return message.to_response_message(result.value.message)

    return None
