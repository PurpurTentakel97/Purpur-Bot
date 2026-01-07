from typing import Optional

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.database.types.twitch_channel import TwitchChannelDB

TABLENAME = "bot_twitch_lookup"


def select_twitch_channels_by_bot_id(bot_id: int) -> list[TwitchChannelDB]:
    return PROGRAMM_PARTS.database.select_all(table_name=TABLENAME, where={"id": bot_id}, type_=TwitchChannelDB)


def insert_twitch_channel(bot_id: int, twitch_channel: str) -> Optional[int]:
    return PROGRAMM_PARTS.database.insert(table_name=TABLENAME, data={"bot_id": bot_id, "channel_name": twitch_channel})


async def delete_twitch_channel(bot_id: int, twitch_channel: str) -> bool:
    return PROGRAMM_PARTS.database.delete(
        table_name=TABLENAME, where={"bot_id": bot_id, "channel_name": twitch_channel}
    )
