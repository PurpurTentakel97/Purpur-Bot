from bot.core.helpers.string import identifier_for_db
from bot.core.helpers.string import strip_for_db
from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.broadcast_messages import FIELD_ENABLED
from bot.database.broadcast_messages import FIELD_INTERVAL_IN_MINUTES
from bot.database.broadcast_messages import FIELD_MESSAGE
from bot.database.broadcast_messages import delete_broadcast_message_by_id as delete_broadcast_message_by_id_db
from bot.database.broadcast_messages import insert_broadcast_message as insert_broadcast_message_db
from bot.database.broadcast_messages import select_all_broadcast_messages as select_all_broadcast_messages_db
from bot.database.broadcast_messages import (
    select_broadcast_message_by_channel_name as select_broadcast_message_by_channel_name_db,
)
from bot.database.broadcast_messages import select_broadcast_message_by_id as select_broadcast_message_by_id_db
from bot.database.broadcast_messages import update_broadcast_message_by_id as update_broadcast_message_by_id_db
from bot.database.types.twitch_broadcast_message import TwitchBroadcastMessageDB


def save_broadcast_message(bot_id: int, channel_name: str, message: str, interval_in_minutes: int) -> Result[int]:
    channel_name_db = identifier_for_db(channel_name)
    message_db = strip_for_db(message)

    result = insert_broadcast_message_db(bot_id, channel_name_db, message_db, interval_in_minutes)

    if result.state.fail or result.value is None:
        return result

    if PROGRAMM_PARTS.broadcast is not None:
        data = get_broadcast_message_by_id(result.value)
        if result.state.fail or data.value is None:
            delete_broadcast_message_by_id(result.value)
            return data.cast_to(int)
        PROGRAMM_PARTS.broadcast.add_or_update_message(data.value)

    return result


def get_broadcast_message_by_id(message_id: int) -> Result[TwitchBroadcastMessageDB]:
    return select_broadcast_message_by_id_db(message_id)


def get_broadcast_message_by_channel_name(bot_id: int, channel_name: str) -> Result[list[TwitchBroadcastMessageDB]]:
    return select_broadcast_message_by_channel_name_db(bot_id, identifier_for_db(channel_name))


def get_all_broadcast_messages() -> Result[list[TwitchBroadcastMessageDB]]:
    return select_all_broadcast_messages_db()


def _update(message_id: int) -> bool:
    data = get_broadcast_message_by_id(message_id)
    if data.state.fail or data.value is None:
        return False

    if PROGRAMM_PARTS.broadcast is None:
        return False

    PROGRAMM_PARTS.broadcast.add_or_update_message(data.value)

    return True


def update_broadcast_message_by_id(
    message_id: int, message: str, interval_in_minutes: int, enabled: bool
) -> Result[None]:
    message_db = strip_for_db(message)

    result = update_broadcast_message_by_id_db(
        message_id, {FIELD_MESSAGE: message_db, FIELD_INTERVAL_IN_MINUTES: interval_in_minutes, FIELD_ENABLED: enabled}
    )
    if result.state.fail:
        return result

    if not _update(message_id):
        return Result(ResultState.ERROR, None)

    return result


def delete_broadcast_message_by_id(message_id: int) -> Result[None]:
    data = get_broadcast_message_by_id(message_id)
    if data.state.fail or data.value is None:
        return data.cast_to(type(None))

    if PROGRAMM_PARTS.broadcast is not None:
        PROGRAMM_PARTS.broadcast.remove_message(data.value.id)

    result = delete_broadcast_message_by_id_db(message_id)
    return result
