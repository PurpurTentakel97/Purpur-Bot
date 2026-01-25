from bot.core.counter import decrement_counter_by
from bot.core.counter import delete_counter
from bot.core.counter import get_counter
from bot.core.counter import get_counter_instructions
from bot.core.counter import has_counter
from bot.core.counter import increment_counter_by
from bot.core.counter import save_counter
from bot.core.helpers.string import check_identifier
from bot.core.helpers.string import check_text
from bot.core.helpers.string import identifier_for_db
from bot.core.types.counter_instructions import CounterOperation
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.commands import delete_command as delete_command_db
from bot.database.commands import delete_command_by_id as delete_command_by_id_db
from bot.database.commands import insert_command as insert_command_db
from bot.database.commands import select_command as select_command_db
from bot.database.commands import select_command_by_id as select_command_by_id_core
from bot.database.commands import select_commands_by_bot_id as select_commands_by_bot_id_db
from bot.database.commands import update_command as update_command_db
from bot.database.commands import update_command_by_id as update_command_by_id_db
from bot.database.types.base_command import BasicCommandDB
from bot.database.types.counter import CounterDB
from bot.database.types.fields import FIELD_BASIC_COMMAND_COMMAND
from bot.database.types.fields import FIELD_BASIC_COMMAND_MESSAGE
from bot.database.types.fields import FIELD_ENABLED


def _replace_counter_and_execute(bot_id: int, message: str) -> str:
    counter = get_counter_instructions(message)

    for c in counter:
        counter_result = get_counter(bot_id, c.name)
        if counter_result.state.fail or counter_result.value is None:
            continue

        if c.value is not None and c.operation is not None:
            if c.operation == CounterOperation.ADD:
                increment_result = increment_counter_by(bot_id, c.name, c.value)
            else:
                increment_result = decrement_counter_by(bot_id, c.name, c.value)
            if increment_result.value is None:
                continue
            counter_result.value.count = increment_result.value.count
            pattern = f"{{{c.name}{c.operation.value}{str(c.value)}}}"
            message = message.replace(pattern, str(counter_result.value.count))

        else:
            pattern = f"{{{c.name}}}"
            message = message.replace(pattern, str(counter_result.value.count))

    return message


def _handle_new_counter(bot_id: int, message: str) -> bool:
    if not has_counter(message):
        return True

    def handle_rollback(bot_id: int, new_counter_names: list[CounterDB]) -> None:
        for c in new_counter_names:
            delete_counter(bot_id, c.name)

    new_counter_names: list[CounterDB] = []
    counter = get_counter_instructions(message)

    for c in counter:
        counter_result = save_counter(bot_id, c.name)
        if counter_result.state == ResultState.ALREADY_EXISTS:
            continue
        if counter_result.state.fail or counter_result.value is None:
            handle_rollback(bot_id, new_counter_names)
            return False
        new_counter_names.append(counter_result.value)

    return True


def get_commands_by_bot_id(bot_id: int) -> Result[list[BasicCommandDB]]:
    return select_commands_by_bot_id_db(bot_id)


def get_command_by_id(command_id: int) -> Result[BasicCommandDB]:
    return select_command_by_id_core(command_id)


def get_command(bot_id: int, name: str) -> Result[BasicCommandDB]:
    return select_command_db(bot_id, identifier_for_db(name))


def get_command_with_counter(bot_id: int, command_name: str) -> Result[BasicCommandDB]:
    command_result = get_command(bot_id, command_name)

    if command_result.state.fail or command_result.value is None:
        return command_result

    if not command_result.value.enabled:
        return Result(ResultState.COMMAND_DISABLED, command_result.value)

    if has_counter(command_result.value.message):
        command_result.value.message = _replace_counter_and_execute(bot_id, command_result.value.message)

    return command_result


def save_command(bot_id: int, name: str, message: str) -> Result[BasicCommandDB]:
    name_db = check_identifier(name)
    message_db = check_text(message)

    if name_db.state.fail or name_db.value is None:
        return name_db.cast_to(BasicCommandDB)

    if message_db.state.fail or message_db.value is None:
        return message_db.cast_to(BasicCommandDB)

    if not _handle_new_counter(bot_id, message_db.value):
        return Result(ResultState.COUNTER_ERROR, None)

    return insert_command_db(bot_id, name_db.value, message_db.value)


def update_command_by_id(
    bot_id: int, command_id: int, name: str, message: str, enabled: bool
) -> Result[BasicCommandDB]:
    name_db = check_identifier(name)
    message_db = check_text(message)

    if name_db.state.fail or name_db.value is None:
        return name_db.cast_to(BasicCommandDB)

    if message_db.state.fail or message_db.value is None:
        return message_db.cast_to(BasicCommandDB)

    if not _handle_new_counter(bot_id, message_db.value):
        return Result(ResultState.COUNTER_ERROR, None)

    return update_command_by_id_db(
        command_id,
        {
            FIELD_BASIC_COMMAND_COMMAND: name_db.value,
            FIELD_BASIC_COMMAND_MESSAGE: message_db.value,
            FIELD_ENABLED: enabled,
        },
    )


def update_command_message(bot_id: int, name: str, message: str) -> Result[BasicCommandDB]:
    message_db = check_text(message)

    if message_db.state.fail or message_db.value is None:
        return message_db.cast_to(BasicCommandDB)

    if not _handle_new_counter(bot_id, message_db.value):
        return Result(ResultState.COUNTER_ERROR, None)

    return update_command_db(bot_id, identifier_for_db(name), {FIELD_BASIC_COMMAND_MESSAGE: message_db.value})


def update_command_name(bot_id: int, old_name: str, new_name: str) -> Result[BasicCommandDB]:
    new_name_db = check_identifier(new_name)
    old_name_db = identifier_for_db(old_name)

    if new_name_db.state.fail or new_name_db.value is None:
        return new_name_db.cast_to(BasicCommandDB)

    return update_command_db(bot_id, old_name_db, {FIELD_BASIC_COMMAND_COMMAND: new_name_db.value})


def enable_command_by_bot_id(bot_id: int, name: str) -> Result[BasicCommandDB]:
    return update_command_db(bot_id, identifier_for_db(name), {FIELD_ENABLED: True})


def disable_command_by_bot_id(bot_id: int, name: str) -> Result[BasicCommandDB]:
    return update_command_db(bot_id, identifier_for_db(name), {FIELD_ENABLED: False})


def delete_command_by_id(command_id: int) -> Result[None]:
    return delete_command_by_id_db(command_id)


def delete_command(bot_id: int, name: str) -> Result[None]:
    return delete_command_db(bot_id, identifier_for_db(name))
