from bot.helpers.log import log_default, LogLevel
from bot.types.chat_message import ChatMessage

def add_command(id_: int, command_name: str, command_message: str) -> None:
    log_default(
        LogLevel.DEBUG, f"command '{command_name}' added: '{command_message}' to id {id_}"
    )

def edit_command(id_: int, command_name: str, command_message: str) -> None:
    log_default(
        LogLevel.DEBUG, f"command '{command_name}' edited: '{command_message}' with id {id_}"
    )

def remove_command(id_: int, command_name: str) -> None:
    log_default(LogLevel.DEBUG, f"command '{command_name}' removed with id {id_}")

def handle_command(message: ChatMessage) -> None:
    parts = message.text.strip().split(" ")
    match parts:
        case ["!command", "add", command_name, *msg]:
            command_message = " ".join(msg)
            if not command_message:
                return
            add_command(message.id_, command_name, command_message)

        case ["!command", "edit", command_name, *msg]:
            command_message = " ".join(msg)
            if not command_message:
                return
            edit_command(message.id_, command_name, command_message)

        case ["!command", "remove", command_name]:
            remove_command(message.id_, command_name)

        case _:
            # todo: look up command
            return
