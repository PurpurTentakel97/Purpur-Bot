from typing import Any

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.database.types.fields import FIELD_BOT_ID
from bot.database.types.fields import FIELD_ID
from bot.database.types.fields import FIELD_TWITCH_CHANNEL_NAME
from bot.database.types.fields import TABLE_TWITCH_NAME
from bot.database.types.twitch_channel import TwitchChannelDB


def select_twitch_channels_by(where: dict[str, Any]) -> Result[list[TwitchChannelDB]]:
    return PROGRAMM_PARTS.database.select_all(table_name=TABLE_TWITCH_NAME, where=where, type_=TwitchChannelDB)


def select_twitch_channel_by(where: dict[str, Any]) -> Result[TwitchChannelDB]:
    return PROGRAMM_PARTS.database.select_one(table_name=TABLE_TWITCH_NAME, where=where, type_=TwitchChannelDB)


def insert_twitch_channel(bot_id: int, twitch_channel: str) -> Result[int]:
    return PROGRAMM_PARTS.database.insert(
        table_name=TABLE_TWITCH_NAME, data={FIELD_BOT_ID: bot_id, FIELD_TWITCH_CHANNEL_NAME: twitch_channel}
    )


def update_twitch_channel_by_id(id_: int, data: dict[str, Any]) -> Result[None]:
    return PROGRAMM_PARTS.database.update(table_name=TABLE_TWITCH_NAME, where={FIELD_ID: id_}, data=data)


def delete_twitch_channel(bot_id: int, twitch_channel: str) -> Result[None]:
    return PROGRAMM_PARTS.database.delete(
        table_name=TABLE_TWITCH_NAME, where={FIELD_BOT_ID: bot_id, FIELD_TWITCH_CHANNEL_NAME: twitch_channel}
    )
