from bot.core.helpers.string import identifier_for_db
from bot.core.helpers.string import strip_for_db
from bot.core.types.result import Result
from bot.core.types.result import ResultState
from bot.database.broadcast_messages import FIELD_INTERVAL_IN_MINUTES
from bot.database.broadcast_messages import FIELD_MESSAGE
from bot.database.broadcast_messages import delete_broadcast_message_by_id as delete_broadcast_message_by_id_db
from bot.database.broadcast_messages import insert_broadcast_message as insert_broadcast_message_db
from bot.database.broadcast_messages import select_all_broadcast_messages as select_all_broadcast_messages_db
from bot.database.broadcast_messages import (
    select_broadcast_message_by_channel_name as select_broadcast_message_by_channel_name_db,
)
from bot.database.broadcast_messages import select_broadcast_message_by_id as select_broadcast_message_by_id_db
from bot.database.broadcast_messages import update_broadcast_message_by_id as update_broadcast_message_message_by_id_db
from bot.database.types.twitch_broadcast_message import TwitchBroadcastMessageDB


def save_broadcast_message(bot_id: int, channel_name: str, message: str, interval_in_minutes: int) -> Result[int]:
    channel_name_db = identifier_for_db(channel_name)
    message_db = strip_for_db(message)

    result = insert_broadcast_message_db(bot_id, channel_name_db, message_db, interval_in_minutes)

    if result.state.fail or result.value is None:
        return result

    data = get_broadcast_message_by_id(result.value)
    if result.state.fail or data.value is None:
        delete_broadcast_message_by_id(result.value)
        return data.cast_to(int)

    # TODO: add new broadcast message to broadcast handler

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

    # TODO: update broadcast message in broadcast handler

    return True


def update_broadcast_message_message_by_id(message_id: int, message: str) -> Result[None]:
    message_db = strip_for_db(message)

    result = update_broadcast_message_message_by_id_db(message_id, {FIELD_MESSAGE: message_db})
    if result.state.fail:
        return result

    if not _update(message_id):
        return Result(ResultState.ERROR, None)

    return result


def update_broadcast_message_interval_by_id(message_id: int, interval_in_minutes: int) -> Result[None]:
    result = update_broadcast_message_message_by_id_db(message_id, {FIELD_INTERVAL_IN_MINUTES: interval_in_minutes})
    if result.state.fail:
        return result

    if not _update(message_id):
        return Result(ResultState.ERROR, None)

    return result


def delete_broadcast_message_by_id(message_id: int) -> Result[None]:
    data = get_broadcast_message_by_id(message_id)
    if data.state.fail or data.value is None:
        return data.cast_to(type(None))

    # TODO: remove broadcast message from broadcast handler

    result = delete_broadcast_message_by_id_db(message_id)
    return result
