from typing import Any

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.database.types.twitch_broadcast_message import TwitchBroadcastMessageDB

TABLE_NAME = "twitch_broadcast_message"
FIELD_MESSAGE = "message"
FIELD_INTERVAL_IN_MINUTES = "interval_in_minutes"


def insert_broadcast_message(bot_int: int, channel_name: str, message: str, interval_in_minutes: int) -> Result[int]:
    return PROGRAMM_PARTS.database.insert(
        table_name=TABLE_NAME,
        data={
            "bot_id": bot_int,
            "channel_name": channel_name,
            "message": message,
            "interval_in_minutes": interval_in_minutes,
        },
    )


def select_broadcast_message_by_id(message_id: int) -> Result[TwitchBroadcastMessageDB]:
    return PROGRAMM_PARTS.database.select_one(
        table_name=TABLE_NAME,
        where={"id": message_id},
        type_=TwitchBroadcastMessageDB,
    )


def select_broadcast_message_by_channel_name(bot_id: int, channel_name: str) -> Result[list[TwitchBroadcastMessageDB]]:
    return PROGRAMM_PARTS.database.select_all(
        TABLE_NAME, {"bot_id": bot_id, "channel_name": channel_name}, TwitchBroadcastMessageDB
    )


def select_all_broadcast_messages() -> Result[list[TwitchBroadcastMessageDB]]:
    return PROGRAMM_PARTS.database.select_all(table_name=TABLE_NAME, where={}, type_=TwitchBroadcastMessageDB)


def update_broadcast_message_by_id(message_id: int, data: dict[str, Any]) -> Result[None]:
    return PROGRAMM_PARTS.database.update(table_name=TABLE_NAME, where={"id": message_id}, data=data)


def delete_broadcast_message_by_id(message_id: int) -> Result[None]:
    return PROGRAMM_PARTS.database.delete(table_name=TABLE_NAME, where={"id": message_id})
