from typing import Optional
from bot.helpers.log import log_default, LogLevel
from bot.types.chat_message import ChatMessage
from bot.types.response_message import ResponseMessage


def add_command(id_: int, command_name: str, command_message: str) -> ResponseMessage:
    log_default(
        LogLevel.DEBUG, f"command '{command_name}' added: '{command_message}' to id {id_}"
    )
    return ResponseMessage()


def edit_command(id_: int, command_name: str, command_message: str) -> ResponseMessage:
    log_default(
        LogLevel.DEBUG, f"command '{command_name}' edited: '{command_message}' with id {id_}"
    )
    return ResponseMessage()


def remove_command(id_: int, command_name: str) -> ResponseMessage:
    log_default(LogLevel.DEBUG, f"command '{command_name}' removed with id {id_}")
    return ResponseMessage()


def try_lookup_command(id_: int, command_name: str) -> Optional[ResponseMessage]:
    return None


def handle_command(message: ChatMessage) -> Optional[ResponseMessage]:
    parts = message.text.strip().split(" ")

    if True:
        # todo: restrict by mod and admin
        match parts:
            case ["!command", "add", command_name, *msg]:
                command_message = " ".join(msg)
                if not command_message:
                    return ResponseMessage()
                return add_command(message.id_, command_name, command_message)

            case ["!command", "edit", command_name, *msg]:
                command_message = " ".join(msg)
                if not command_message:
                    return ResponseMessage()
                return edit_command(message.id_, command_name, command_message)

            case ["!command", "remove", command_name]:
                return remove_command(message.id_, command_name)

            case _:
                pass

    return try_lookup_command(message.id_, parts[0])
