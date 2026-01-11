from typing import Any

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.database.types.twitch_channel import TwitchChannelDB

TABLENAME = "bot_twitch_lookup"
FIELD_CHANNEL_NAME = "channel_name"


def select_twitch_channels_by_bot_id(bot_id: int) -> Result[list[TwitchChannelDB]]:
    return PROGRAMM_PARTS.database.select_all(table_name=TABLENAME, where={"id": bot_id}, type_=TwitchChannelDB)


def select_twitch_channel_by(where: dict[str, Any]) -> Result[TwitchChannelDB]:
    return PROGRAMM_PARTS.database.select_one(table_name=TABLENAME, where=where, type_=TwitchChannelDB)


def insert_twitch_channel(bot_id: int, twitch_channel: str) -> Result[int]:
    return PROGRAMM_PARTS.database.insert(table_name=TABLENAME, data={"bot_id": bot_id, "channel_name": twitch_channel})


def delete_twitch_channel(bot_id: int, twitch_channel: str) -> Result[None]:
    return PROGRAMM_PARTS.database.delete(
        table_name=TABLENAME, where={"bot_id": bot_id, "channel_name": twitch_channel}
    )
