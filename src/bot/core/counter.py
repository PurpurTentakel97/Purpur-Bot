import re
from typing import Optional

from bot.core.helpers.string import check_identifier
from bot.core.helpers.string import identifier_for_db
from bot.core.types.counter_instructions import CounterInstructions
from bot.core.types.counter_instructions import CounterOperation
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.commands import select_commands_by_bot_id as select_commands_by_bot_id_db
from bot.database.commands import update_command as update_command_db
from bot.database.counter import delete_counter as delete_counter_db
from bot.database.counter import delete_counter_by_id as delete_counter_by_id_db
from bot.database.counter import insert_counter as insert_counter_db
from bot.database.counter import select_counter as select_counter_db
from bot.database.counter import select_counter_by_bot_id as select_counter_by_bot_id_db
from bot.database.counter import select_counter_by_id as select_counter_by_id_db
from bot.database.counter import update_counter as update_counter_db
from bot.database.counter import update_counter_by_id as update_counter_by_id_db
from bot.database.types.base_command import BasicCommandDB
from bot.database.types.counter import CounterDB
from bot.database.types.fields import FIELD_BASIC_COMMAND_MESSAGE
from bot.database.types.fields import FIELD_COUNTER_COUNT
from bot.database.types.fields import FIELD_COUNTER_NAME

_COUNTER_PATTERN = re.compile(r"\{(?P<name>[a-zA-ZäöüÄÖÜ]\w*)(?:(?P<op>[+-])(?P<value>\d+))?\}")


def _update_counter_names_in_commands(
    bot_id: int,
    old_counter_name: str,
    new_counter_name: str,
    handle_rollback: bool = True,
    handled_commands: Optional[list[BasicCommandDB]] = None,
) -> bool:
    if handled_commands is None:
        handled_commands = []

    commands_result = select_commands_by_bot_id_db(bot_id)
    if commands_result.state.fail and commands_result.state != ResultState.NO_DATA:
        return False

    if commands_result.value is None or len(commands_result.value) == 0:
        return True

    for command in commands_result.value:
        if has_counter(command.message):
            instructions = get_counter_instructions(command.message)
            for instruction in instructions:
                if instruction.name == old_counter_name:
                    if instruction.operation and instruction.value:
                        pattern = f"{{{old_counter_name}{instruction.operation.value}{str(instruction.value)}}}"
                        command.message = command.message.replace(
                            pattern, f"{{{new_counter_name}{instruction.operation.value}{str(instruction.value)}}}"
                        )
                    else:
                        pattern = f"{{{old_counter_name}}}"
                        command.message = command.message.replace(pattern, f"{{{new_counter_name}}}")

                    update_result = update_command_db(
                        bot_id, command.command, {FIELD_BASIC_COMMAND_MESSAGE: command.message}
                    )
                    handled_commands.append(command)
                    if update_result.state.fail:
                        if handle_rollback:
                            _update_counter_names_in_commands(
                                bot_id, new_counter_name, old_counter_name, False, handled_commands
                            )
                        return False

    return True


def _can_counter_be_deleted(bot_id: int, counter_name: str) -> bool:
    commands_result = select_commands_by_bot_id_db(bot_id)
    if commands_result.state.fail and commands_result.state != ResultState.NO_DATA:
        return False

    if commands_result.value is None or len(commands_result.value) == 0:
        return True

    for command in commands_result.value:
        if has_counter(command.message):
            instructions = get_counter_instructions(command.message)
            for instruction in instructions:
                if instruction.name == counter_name:
                    return False

    return True


def has_counter(message: str) -> bool:
    return _COUNTER_PATTERN.search(message) is not None


def get_counter_instructions(message: str) -> list[CounterInstructions]:
    output: list[CounterInstructions] = []

    for match in _COUNTER_PATTERN.finditer(message):
        name = str(match.group("name"))
        op_raw = match.group("op")
        value_raw = match.group("value")

        if op_raw and value_raw:
            op = CounterOperation(op_raw)
            value = int(value_raw)
            if value != 0:
                output.append(CounterInstructions(name, op, value))

        output.append(CounterInstructions(name, None, None))

    return output


def get_counters_by_bot_id(bot_id: int) -> Result[list[CounterDB]]:
    return select_counter_by_bot_id_db(bot_id)


def get_counter_by_id(counter_id: int) -> Result[CounterDB]:
    return select_counter_by_id_db(counter_id)


def get_counter(bot_id: int, name: str) -> Result[CounterDB]:
    return select_counter_db(bot_id, identifier_for_db(name))


def save_counter(bot_id: int, name: str) -> Result[CounterDB]:
    name_db = check_identifier(name)

    if name_db.state.fail or name_db.value is None:
        return name_db.cast_to(CounterDB)

    return insert_counter_db(bot_id, name_db.value)


def edit_counter_name(bot_id: int, old_name: str, new_name: str) -> Result[CounterDB]:
    new_name_res = check_identifier(new_name)
    old_name_db = identifier_for_db(old_name)

    def handle_rollback(bot_id: int, old_name_db: str, new_name_db: str) -> None:
        update_counter_db(bot_id, new_name_db, {FIELD_COUNTER_NAME: old_name_db})

    if new_name_res.state.fail or new_name_res.value is None:
        return new_name_res.cast_to(CounterDB)

    new_name_db = new_name_res.value
    counter_result = update_counter_db(bot_id, old_name_db, {FIELD_COUNTER_NAME: new_name_db})

    if counter_result.state.fail:
        return counter_result

    if not _update_counter_names_in_commands(bot_id, old_name_db, new_name_db):
        handle_rollback(bot_id, old_name_db, new_name_db)
        return Result(ResultState.COUNTER_ERROR, None)

    return counter_result


def edit_counter_value_by_id(counter_id: int, value: int) -> Result[CounterDB]:
    return update_counter_by_id_db(counter_id, {FIELD_COUNTER_COUNT: value})


def update_counter_by_id(counter_id: int, name: str, count: int) -> Result[CounterDB]:
    name_res = check_identifier(name)

    if name_res.state.fail or name_res.value is None:
        return name_res.cast_to(CounterDB)

    new_name_db = name_res.value

    counter_result = get_counter_by_id(counter_id)
    if counter_result.state.fail or counter_result.value is None:
        return counter_result

    old_name_db = counter_result.value.name
    bot_id = counter_result.value.bot_id

    def handle_rollback(bot_id: int, counter_id: int, old_name_db: str, old_count: int) -> None:
        update_counter_by_id_db(counter_id, {FIELD_COUNTER_NAME: old_name_db, FIELD_COUNTER_COUNT: old_count})

    update_result = update_counter_by_id_db(counter_id, {FIELD_COUNTER_NAME: new_name_db, FIELD_COUNTER_COUNT: count})

    if update_result.state.fail:
        return update_result

    if old_name_db != new_name_db:
        if not _update_counter_names_in_commands(bot_id, old_name_db, new_name_db):
            handle_rollback(bot_id, counter_id, old_name_db, counter_result.value.count)
            return Result(ResultState.COUNTER_ERROR, None)

    return update_result


def edit_counter_value(bot_id: int, name: str, value: int) -> Result[CounterDB]:
    return update_counter_db(bot_id, identifier_for_db(name), {FIELD_COUNTER_COUNT: value})


def reset_counter_by_id(counter_id: int) -> Result[CounterDB]:
    return edit_counter_value_by_id(counter_id, 0)


def reset_counter(bot_id: int, name: str) -> Result[CounterDB]:
    return edit_counter_value(bot_id, identifier_for_db(name), 0)


def increment_counter_by(bot_id: int, name: str, offset: int) -> Result[CounterDB]:
    name_db = identifier_for_db(name)
    get_result = get_counter(bot_id, name_db)

    if get_result.state.fail or get_result.value is None:
        return get_result

    new_value = get_result.value.count + offset

    update_result = edit_counter_value(bot_id, name_db, new_value)

    if update_result.state.fail:
        return update_result.cast_to(CounterDB, None)

    get_result.value.count = new_value
    return update_result.cast_to(CounterDB, get_result.value)


def increment_counter(bot_id: int, name: str) -> Result[CounterDB]:
    return increment_counter_by(bot_id, name, 1)  # name will be handled in increment_counter_by


def decrement_counter_by(bot_id: int, name: str, offset: int) -> Result[CounterDB]:
    return increment_counter_by(bot_id, name, -offset)  # name will be handled in increment_counter_by


def decrement_counter(bot_id: int, name: str) -> Result[CounterDB]:
    return increment_counter_by(bot_id, name, -1)  # name will be handled in increment_counter_by


def delete_counter_by_id(counter_id: int) -> Result[None]:
    counter_result = get_counter_by_id(counter_id)
    if counter_result.state.fail or counter_result.value is None:
        return Result(counter_result.state, None)

    if not _can_counter_be_deleted(counter_result.value.bot_id, counter_result.value.name):
        return Result(ResultState.STILL_IN_USE, None)

    return delete_counter_by_id_db(counter_id)


def delete_counter(bot_id: int, name: str) -> Result[None]:
    name_db = identifier_for_db(name)

    if not _can_counter_be_deleted(bot_id, name_db):
        return Result(ResultState.STILL_IN_USE, None)

    return delete_counter_db(bot_id, name_db)
