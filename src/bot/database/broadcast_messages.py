from typing import Any

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.database.types.fields import FIELD_BOT_ID
from bot.database.types.fields import FIELD_ID
from bot.database.types.fields import FIELD_TWITCH_BROADCAST_INTERVAL_IN_MINUTES
from bot.database.types.fields import FIELD_TWITCH_BROADCAST_MESSAGE
from bot.database.types.fields import FIELD_TWITCH_CHANNEL_NAME
from bot.database.types.fields import TABLE_TWITCH_BROADCAST_NAME
from bot.database.types.twitch_broadcast_message import TwitchBroadcastMessageDB


def insert_broadcast_message(bot_int: int, channel_name: str, message: str, interval_in_minutes: int) -> Result[int]:
    return PROGRAMM_PARTS.database.insert(
        table_name=TABLE_TWITCH_BROADCAST_NAME,
        data={
            FIELD_BOT_ID: bot_int,
            FIELD_TWITCH_CHANNEL_NAME: channel_name,
            FIELD_TWITCH_BROADCAST_MESSAGE: message,
            FIELD_TWITCH_BROADCAST_INTERVAL_IN_MINUTES: interval_in_minutes,
        },
    )


def select_broadcast_message_by_id(message_id: int) -> Result[TwitchBroadcastMessageDB]:
    return PROGRAMM_PARTS.database.select_one(
        table_name=TABLE_TWITCH_BROADCAST_NAME,
        where={FIELD_ID: message_id},
        type_=TwitchBroadcastMessageDB,
    )


def select_broadcast_message_by_channel_name(bot_id: int, channel_name: str) -> Result[list[TwitchBroadcastMessageDB]]:
    return PROGRAMM_PARTS.database.select_all(
        TABLE_TWITCH_BROADCAST_NAME,
        {FIELD_BOT_ID: bot_id, FIELD_TWITCH_CHANNEL_NAME: channel_name},
        TwitchBroadcastMessageDB,
    )


def select_all_broadcast_messages() -> Result[list[TwitchBroadcastMessageDB]]:
    return PROGRAMM_PARTS.database.select_all(
        table_name=TABLE_TWITCH_BROADCAST_NAME, where={}, type_=TwitchBroadcastMessageDB
    )


def update_broadcast_message_by_id(message_id: int, data: dict[str, Any]) -> Result[None]:
    return PROGRAMM_PARTS.database.update(
        table_name=TABLE_TWITCH_BROADCAST_NAME, where={FIELD_ID: message_id}, data=data
    )


def delete_broadcast_message_by_id(message_id: int) -> Result[None]:
    return PROGRAMM_PARTS.database.delete(table_name=TABLE_TWITCH_BROADCAST_NAME, where={FIELD_ID: message_id})
