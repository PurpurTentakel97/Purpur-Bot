from typing import Any

from bot.core.types.programm_parts import PROGRAMM_PARTS
from bot.core.types.result import Result
from bot.database.types.feature_flags import TwitchFeatureFlagsDB
from bot.database.types.fields import FIELD_BOT_ID
from bot.database.types.fields import FIELD_ID
from bot.database.types.fields import FIELD_TWITCH_CHANNEL_NAME
from bot.database.types.fields import TABLE_TWITCH_FEATURE_FLAGS_NAME


def insert_twitch_feature_flags(bot_id: int, channel_name: str) -> Result[int]:
    return PROGRAMM_PARTS.database.insert(
        table_name=TABLE_TWITCH_FEATURE_FLAGS_NAME, data={FIELD_BOT_ID: bot_id, FIELD_TWITCH_CHANNEL_NAME: channel_name}
    )


def select_twitch_feature_flags_by_id(feature_flag_id: int) -> Result[TwitchFeatureFlagsDB]:
    return PROGRAMM_PARTS.database.select_one(
        table_name=TABLE_TWITCH_FEATURE_FLAGS_NAME, where={FIELD_ID: feature_flag_id}, type_=TwitchFeatureFlagsDB
    )


def select_twitch_feature_flags_by_channel_name(bot_id: int, channel_name: str) -> Result[TwitchFeatureFlagsDB]:
    return PROGRAMM_PARTS.database.select_one(
        table_name=TABLE_TWITCH_FEATURE_FLAGS_NAME,
        where={FIELD_BOT_ID: bot_id, FIELD_TWITCH_CHANNEL_NAME: channel_name},
        type_=TwitchFeatureFlagsDB,
    )


def update_twitch_feature_flags_by_id(feature_flag_id: int, data: dict[str, Any]) -> Result[None]:
    return PROGRAMM_PARTS.database.update(
        table_name=TABLE_TWITCH_FEATURE_FLAGS_NAME, where={FIELD_ID: feature_flag_id}, data=data
    )
