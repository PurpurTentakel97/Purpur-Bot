from bot.database.database import DATABASE
from bot.database.database import DatabaseDeleteData
from bot.database.database import DatabaseGetData
from bot.database.database import DatabaseSaveData
from bot.database.database import DatabaseUpdateData
from bot.types.chat_message import ChatMessage
from bot.types.response_message import ResponseMessage

TABLE_NAME = "basic_commands"


def add_command(message: ChatMessage, command_name: str, command_message: str) -> ResponseMessage:
    data = DatabaseSaveData(
        table_name=TABLE_NAME, data={"id": message.id_, "name": command_name, "message": command_message}
    )
    DATABASE.save(data)
    return ResponseMessage("TODO: add_command_response", message.sender_chat, message.meta_data)


def edit_command(message: ChatMessage, command_name: str, command_message: str) -> ResponseMessage:
    data = DatabaseUpdateData(
        table_name=TABLE_NAME, data={"message": command_message}, where={"id": message.id_, "name": command_name}
    )
    DATABASE.update(data)
    return ResponseMessage("TODO: edit_command_response", message.sender_chat, message.meta_data)


def remove_command(message: ChatMessage, command_name: str) -> ResponseMessage:
    data = DatabaseDeleteData(table_name=TABLE_NAME, where={"id": message.id_, "name": command_name})
    DATABASE.delete(data)
    return ResponseMessage("TODO: edit_command_response", message.sender_chat, message.meta_data)


def try_lookup_command(message: ChatMessage, command_name: str) -> ResponseMessage:
    data = DatabaseGetData(
        table_name=TABLE_NAME, keys=["message"], where={"id": message.id_, "name": command_name.lstrip("!")}
    )
    value = DATABASE.get_single(data, "")

    if value is None:
        return ResponseMessage(f"no command {command_name} present.", message.sender_chat, message.meta_data)
    return ResponseMessage(value, message.sender_chat, message.meta_data)


def handle_command(message: ChatMessage) -> ResponseMessage:
    parts = message.text.strip().split(" ")

    if True:
        # todo: restrict by mod and admin
        match parts:
            case ["!command", "add", command_name, *msg]:
                command_message = " ".join(msg)
                if not command_message:
                    return ResponseMessage(
                        "There was no message provided after the command name.", message.sender_chat, message.meta_data
                    )
                return add_command(message, command_name, command_message)

            case ["!command", "edit", command_name, *msg]:
                command_message = " ".join(msg)
                if not command_message:
                    return ResponseMessage(
                        "There was no message provided after the command name.", message.sender_chat, message.meta_data
                    )
                return edit_command(message, command_name, command_message)

            case ["!command", "remove", command_name]:
                return remove_command(message, command_name)

            case _:
                pass

    return try_lookup_command(message, parts[0])
